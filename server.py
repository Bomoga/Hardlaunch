from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
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
from agents.business_planning_agent import business_planning_agent
from agents.funding_research_agent import funding_research_agent
from agents.market_analysis_agent import market_analysis_agent
from agents.engineering_agent import engineering_agent
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
    
    print(f"\n🔍 DEBUG: Session {session.id}")
    print(f"🔍 DEBUG: Has summary: {has_summary}")
    print(f"🔍 DEBUG: Agent type requested: {payload.agent_type}")
    if summary_record:
        print(f"🔍 DEBUG: Summary content: {summary_record.get('summary', '')[:200]}...")

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
    
    # Route directly to specialized agents when agent_type is specified
    if payload.agent_type and summary_record:
        agent_map = {
            'business': business_planning_agent,
            'finance': funding_research_agent,
            'market': market_analysis_agent,
            'engineering': engineering_agent,
        }
        agent = agent_map.get(payload.agent_type, context_manager_agent)
        
        # Prepend the business summary context to EVERY message
        summary_text = summary_record.get('summary', '')
        query_message = f"""BUSINESS CONTEXT (Use this information as the foundation for your response):
{summary_text}

USER REQUEST: {payload.message}

IMPORTANT: Base your response on the business context provided above. Refer to specific details from the business summary in your answer."""
        print(f"🔍 DEBUG: Injected summary into message for {payload.agent_type} agent")
    else:
        agent = context_manager_agent if has_summary else survey_agent
        query_message = payload.message
        if payload.agent_type and not summary_record:
            print(f"⚠️ WARNING: Agent type '{payload.agent_type}' requested but no summary available!")
    
    runner = Runner(agent=agent, session_service=session_service, app_name=APP_NAME)

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
        # Get the latest session
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
        
        # Mark as submitted and update timestamp
        summary_record["submitted"] = True
        summary_record["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Create a new session object with updated state
        from google.adk.sessions.types import Session
        updated_session = Session(
            id=session.id,
            user_id=session.user_id,
            state={**session.state, BUSINESS_SUMMARY_KEY: summary_record},
            events=session.events,
            created_at=session.created_at,
        )
        
        # Update the session in the service
        await session_service.update_session(updated_session)
        
        # Verify it worked
        verify_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=session_id,
            session_id=session_id,
        )
        verify_record = verify_session.state.get(BUSINESS_SUMMARY_KEY)
        
        if verify_record and verify_record.get("submitted"):
            return {"success": True, "message": "Business summary submitted successfully"}
        else:
            return {"success": False, "message": "Submission failed to persist"}
            
    except Exception as e:
        print(f"Submit error: {e}")
        import traceback
        traceback.print_exc()
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
