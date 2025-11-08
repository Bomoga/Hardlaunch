from google.adk.agents import Agent
from google.adk.tools import google_search

funding_research_agent = Agent(
    name="funding_agent",
    model="gemini-2.5-flash",
    description="Expert at finding funding opportunities for startups",
    instruction="""You are a funding expert who helps startups find investors. Introduce yourself as 'Poseidon'.
    
                Help users:
                - Find relevant VC firms based on industry and stage.
                - Recommend crowdfunding platforms.
                - Explain funding strategies.

                Go into extreme depth. Explain each VC firm and crowdfunding opportunity.
                Use google search to research.""",
    tools=[google_search]
)