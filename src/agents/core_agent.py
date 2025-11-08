from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .business_planning_agent import business_planning_agent
from .funding_research_agent import funding_research_agent
from .market_analysis_agent import market_analysis_agent

core_agent = Agent(
    name="Hardlaunch_Orchestrator",
    model="gemini-2.5-flash",
    description="AI copilot for aspiring startup founders",  
    instruction="""
                You are a request router. Your job is to analyze a user's query and decide which of the following agents or workflows is best suited to handle it.
                Do not answer the query yourself, only return the name of the most appropriate choice.

                Available Options:
                - 'Zeus': The business planning agent, for queries regarding startup design, development, and launching.
                - 'Poseidon': The funding research agent, for queries regarding ways to fund the startup, such as VCs or crowdfunding.
                - 'Ares': The market analysis agent, for queries regarding extensive market analysis and economic discussion.

                Only return the single, most appropriate option's name and nothing else.
                """,
    tools=[
        AgentTool(business_planning_agent),
        AgentTool(funding_research_agent),
        AgentTool(market_analysis_agent),
    ],
)

__all__ = ["root_agent"]
