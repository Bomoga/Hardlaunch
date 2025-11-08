from __future__ import annotations

from typing import Dict

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools import google_search


def analyze_market_trends(industry: str) -> Dict[str, str]:
    """Return qualitative market trends for a given industry."""
    trends = {
        "edtech": {
            "growth_drivers": "Remote learning adoption, personalized tutoring demand",
            "risks": "High competition, regulatory compliance for minors",
            "key_metrics": "Monthly active learners, completion rates, retention",
        },
        "ai tutoring": {
            "growth_drivers": "Advances in LLMs, shortage of qualified tutors",
            "risks": "Trust and safety concerns, data privacy obligations",
            "key_metrics": "Learning outcome improvement, engagement duration",
        },
    }
    industry_key = industry.lower()
    selected = trends.get(
        industry_key,
        {
            "growth_drivers": "Digital transformation and customer demand shifts",
            "risks": "Emerging competitors, macroeconomic uncertainty",
            "key_metrics": "Customer acquisition cost, retention, gross margin",
        },
    )
    return selected


market_analysis_agent = Agent(
    name="market_analysis_agent",
    model="gemini-2.5-flash",
    description="Summarizes industry trends and key market signals.",
    instruction="Introduce yourself as 'Ares'. Provide concise, actionable market context for founders. Use google search to gather information.",
    tools=[google_search],
)

__all__ = ["market_analysis_agent", "analyze_market_trends"]
