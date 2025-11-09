from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.genai.types import Content, Part

from agents.survey_agent import survey_agent
from agents.context_manager_agent import context_manager_agent
from tools.context_memory_tools import BUSINESS_SUMMARY_KEY

app = FastAPI(title="HardLaunch")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()
APP_NAME = "Hardlaunch"

async def run_agent_query(
    runner: Runner,
    query: str,
    session: Session,
    user_id: str,
    verbose: bool = False,
):
    final_response = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=Content(parts=[Part(text=query)], role="user"),
        ):
            if verbose:
                print(f"EVENT: {event}")

            if event.is_final_response():
                if event.content and event.content.parts and len(event.content.parts) > 0:
                    final_response = event.content.parts[0].text
                else:
                    final_response = "I apologize, but I encountered an issue processing your request. Please try again."
                
    except Exception as e:
        final_response = f"An error occurred: {e}"
        print(f"Error in run_agent_query: {e}")

    if verbose:
        print("\n" + "-" * 50)
        print("✅ Final Response:")
        print(final_response)
        print("-" * 50 + "\n")

    return final_response

async def get_or_create_session(session_id: str | None) -> Session:
    if session_id:
        try:
            existing = await session_service.get_session(
                app_name=APP_NAME, user_id=session_id, session_id=session_id
            )
            if existing:
                return existing
        except:
            pass
    return await session_service.create_session(app_name=APP_NAME, user_id=session_id or "anon")

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    agent_type: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    response: str
    summary: Optional[dict] = None

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    session = await get_or_create_session(payload.session_id)
    
    latest_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=session.user_id,
        session_id=session.id,
    )
    summary_record = latest_session.state.get(BUSINESS_SUMMARY_KEY)
    has_summary = bool(summary_record)
    is_submitted = summary_record.get("submitted", False) if summary_record else False

    if not has_summary and not latest_session.events:
        auto_runner = Runner(
            agent=survey_agent,
            session_service=session_service,
            app_name=APP_NAME,
        )
        await run_agent_query(
            runner=auto_runner,
            query="__AUTO_START__",
            session=session,
            user_id=session.user_id,
        )

    if payload.agent_type and not is_submitted:
        return ChatResponse(
            session_id=session.id,
            response="Please complete and submit the initial business survey before using specialized agents. Visit the survey page to get started.",
            summary=None
        )
    
    agent = context_manager_agent if has_summary else survey_agent
    runner = Runner(agent=agent, session_service=session_service, app_name=APP_NAME)
    
    query_message = payload.message
    if payload.agent_type and has_summary:
        agent_prefixes = {
            'business': 'As the Business Planning Agent, ',
            'finance': 'As the Financial Research Agent, ',
            'market': 'As the Market Analytics Agent, ',
            'engineering': 'As the Engineering & Development Agent, '
        }
        prefix = agent_prefixes.get(payload.agent_type, '')
        query_message = f"{prefix}{payload.message}"

    response_text = await run_agent_query(
        runner=runner,
        query=query_message,
        session=session,
        user_id=session.user_id,
        verbose=True,
    )

    latest_session = await session_service.get_session(
        app_name=APP_NAME, user_id=session.user_id, session_id=session.id
    )
    summary = latest_session.state.get(BUSINESS_SUMMARY_KEY)

    return ChatResponse(
        session_id=session.id,
        response=response_text,
        summary=summary,
    )

@app.get("/")
async def root():
    return FileResponse("static/dashboard.html")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "gemini_configured": bool(os.getenv("GEMINI_API_KEY"))}

@app.post("/api/submit-summary")
async def submit_summary(payload: dict):
    """Manually submit the business summary."""
    session_id = payload.get("session_id")
    
    if not session_id:
        return {"success": False, "message": "No session ID provided"}
    
    try:
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=session_id,
            session_id=session_id,
        )
        
        if not session:
            return {"success": False, "message": "Session not found"}
        
        summary_record = session.state.get(BUSINESS_SUMMARY_KEY)
        
        if not summary_record:
            return {"success": False, "message": "No business summary to submit"}
        
        # Mark as submitted
        summary_record["submitted"] = True
        session.state[BUSINESS_SUMMARY_KEY] = summary_record
        
        await session_service.update_session(session)
        
        return {"success": True, "message": "Business summary submitted successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error submitting summary: {str(e)}"}

@app.get("/api/submission-status")
async def submission_status(session_id: Optional[str] = None):
    """Check if the business summary has been submitted for a given session."""
    if not session_id:
        return {
            "submitted": False,
            "has_summary": False,
            "message": "No session ID provided"
        }
    
    try:
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=session_id,
            session_id=session_id,
        )
        
        if not session:
            return {
                "submitted": False,
                "has_summary": False,
                "message": "Session not found"
            }
        
        summary_record = session.state.get(BUSINESS_SUMMARY_KEY)
        
        if not summary_record:
            return {
                "submitted": False,
                "has_summary": False,
                "message": "No business summary found"
            }
        
        is_submitted = summary_record.get("submitted", False)
        
        return {
            "submitted": is_submitted,
            "has_summary": True,
            "message": "Submission status retrieved successfully"
        }
    except Exception as e:
        return {
            "submitted": False,
            "has_summary": False,
            "message": f"Error retrieving submission status: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
