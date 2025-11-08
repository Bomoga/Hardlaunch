import asyncio
import os

from dotenv import load_dotenv
from IPython.display import display, Markdown
import google.generativeai as genai
from google.genai.types import Content, Part
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session

from agents.core_agent import core_agent

session_service = InMemorySessionService()
user_id = "user_001"

async def run_agent_query(agent: Agent, query: str, session: Session, user_id: str, is_router: bool = False):
    """Initializes a runner and executes a query for a given agent and session."""
    print(f"\n Running query for agent: '{agent.name}' in session: '{session.id}'...")

    runner = Runner(
        agent = agent,
        session_service = session_service,
        app_name = agent.name
    )

    final_response = ""
    try:
        async for event in runner.run_async(
            user_id = user_id,
            session_id = session.id,
            new_message = Content(parts = [Part(text = query)], role = "user")
        ):
            if not is_router:
                print(f"EVENT: {event}")

            if event.is_final_response():
                final_response = event.content.parts[0].text
                
    except Exception as e:
        final_response = f"An error occurred: {e}"

    if not is_router:
     print("\n" + "-"*50)
     print("✅ Final Response:")
     print(final_response)
     print("-"*50 + "\n")

    return final_response

async def run_root_agent():
    session = await session_service.create_session(
        app_name = core_agent.name,
        user_id = user_id
    )
    while True:
        query = input("You: ").strip()
        if query.lower() in {"quit", "exit"}:
            break
        response = await run_agent_query(core_agent, query, session, user_id, is_router=True)
        print(f"Hardlaunch: {response}")

async def main() -> None:
    load_dotenv()
    gemini_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key = gemini_key)

    await run_root_agent()

if __name__ == "__main__":
    asyncio.run(main())
