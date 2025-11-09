from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_methods=["*"],
    allow_headers=["*"],
)

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.genai.types import Content, Part

from .agents.onboarding_agent import onboarding_agent
from .agents.context_manager_agent import context_manager_agent
from .tools.context_memory_tools import BUSINESS_SUMMARY_KEY

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
                final_response = event.content.parts[0].text
                
    except Exception as e:
        final_response = f"An error occurred: {e}"

    if verbose:
        print("\n" + "-" * 50)
        print("✅ Final Response:")
        print(final_response)
        print("-" * 50 + "\n")

    return final_response

async def get_or_create_session(session_id: str | None) -> Session:
    if session_id:
        existing = await session_service.get_session(
            app_name=APP_NAME, user_id=session_id, session_id=session_id
        )
        if existing:
            return existing
    return await session_service.create_session(app_name=APP_NAME, user_id=session_id or "anon")

from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    response: str
    summary: dict | None

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    session = await get_or_create_session(payload.session_id)
    
    latest_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=session.user_id,
        session_id=session.id,
    )
    has_summary = bool(latest_session.state.get(BUSINESS_SUMMARY_KEY))

    if not has_summary and not latest_session.events:
        auto_runner = Runner(
            agent=onboarding_agent,
            session_service=session_service,
            app_name=APP_NAME,
        )
        await run_agent_query(
            runner=auto_runner,
            query="__AUTO_START__",
            session=session,
            user_id=session.user_id,
        )

    agent = context_manager_agent if has_summary else onboarding_agent
    runner = Runner(agent=agent, session_service=session_service, app_name=APP_NAME)

    response_text = await run_agent_query(
        runner=runner,
        query=payload.message,
        session=session,
        user_id=session.user_id,
        verbose=False,
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
