from google.adk.agents import SequentialAgent
from agents.survey_agent import survey_agent
from agents.context_manager_agent import context_manager_agent

onboarding_agent = SequentialAgent(
    name="onboarding_agent",
    sub_agents=[survey_agent, context_manager_agent],
    description="Initiates survey to home page agent workflow."
)