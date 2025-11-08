import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.genai.types import Content, Part
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session

from agents.context_manager_agent import context_manager_agent
from agents.onboarding_agent import onboarding_agent

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

APP_NAME = "Hardlaunch"
USER_ID = "user_001"
session_service = InMemorySessionService()

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

async def run_onboarding(session: Session) -> Runner:
    """
    Runs the onboarding workflow (survey -> context manager transition).
    Returns a Runner with context_manager_agent as root for subsequent use.
    """
    print("\nStarting onboarding workflow...\n")
    
    # Create runner with onboarding workflow
    onboarding_runner = Runner(
        agent=onboarding_agent,
        session_service=session_service,
        app_name=APP_NAME,
    )

    # Continue interactive survey until completion
    survey_complete = False
    while not survey_complete:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in {"quit", "exit"}:
            print("Exiting onboarding. You can resume later.")
            return None
        
        response = await run_agent_query(
            runner=onboarding_runner,
            session=session,
            user_id=USER_ID,
            query=user_input,
            verbose=False
        )
        
        print(f"Hardlaunch: {response}\n")
        
        # Check if business_summary exists in state (survey completed)
        current_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session.id
        )
        
        if current_session.state.get("business_summary"):
            survey_complete = True
            print("\nSurvey completed! Transitioning to Context Manager...\n")
    
    # After onboarding, create new runner with context_manager as root
    context_runner = Runner(
        agent=context_manager_agent,
        session_service=session_service,
        app_name=APP_NAME,
    )
    
    return context_runner

async def run_interactive_session(runner: Runner, session: Session):
    """
    Runs the main interactive loop with context_manager_agent as root.
    Handles user queries, restart command, and summary display.
    """
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        
        # Exit command
        if user_input.lower() in {"quit", "exit"}:
            print("\n👋 Thank you for using Hardlaunch! Goodbye.\n")
            break
        
        # Display summary command
        if user_input.lower() == "summary":
            # await display_business_summary(session)
            continue
        
        # Restart survey command
        if user_input.lower() == "restart":
            print("\n🔄 Restarting business survey...\n")
            
            # Clear business_summary from state
            session.state.pop("business_summary", None)
            
            # Re-run onboarding workflow
            new_runner = await run_onboarding(session)
            
            if new_runner:
                runner = new_runner  # Update runner reference
                print("\nSurvey restarted and completed! You're back in the main session.\n")
            else:
                print("\nOnboarding was interrupted. Continuing with previous session.\n")
            
            continue
        
        # Normal query handling
        response = await run_agent_query(
            runner=runner,
            session=session,
            user_id=USER_ID,
            query=user_input,
            verbose=False
        )
        
        print(f"Hardlaunch: {response}\n")

def print_session_info(session: Session, is_new: bool):
    """Prints session information."""
    status = "New Session Created" if is_new else "Existing Session Loaded"
    print(f"\n📋 Session Info:")
    print(f"   Status: {status}")
    print(f"   Session ID: {session.id}")
    print(f"   App: {APP_NAME}")
    print(f"   User: {USER_ID}\n")

async def main() -> None:
    """Main application entry point."""
    
    # Initialize session
    # Check if user has existing sessions
    existing_sessions = session_service.list_sessions(
        app_name=APP_NAME,
        user_id=USER_ID
    )
    
    if existing_sessions and len(existing_sessions) > 0:
        # Load existing session
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=existing_sessions[0].id
        )
        print_session_info(session, is_new=False)
        
        # Check if onboarding was completed
        if not session.state.get("business_summary"):
            print("Previous session found but survey incomplete. Starting onboarding...\n")
            runner = await run_onboarding(session)
        else:
            print("Resuming with existing business summary.\n")
            # Create runner with context_manager as root
            runner = Runner(
                agent=context_manager_agent,
                session_service=session_service,
                app_name=APP_NAME,
            )
    else:
        # Create new session for new user
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
        )
        print_session_info(session, is_new=True)
        
        # Run onboarding workflow
        runner = await run_onboarding(session)
    
    # If onboarding was successful, start interactive session
    if runner:
        await run_interactive_session(runner, session)
    else:
        print("\nSession initialization failed or was interrupted.\n")

if __name__ == "__main__":
    asyncio.run(main())
