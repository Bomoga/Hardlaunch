from __future__ import annotations

from typing import Dict

from google.adk.agents import Agent
from google.adk.tools import FunctionTool, google_search


def generate_business_canvas(industry: str, target_customer: str) -> Dict[str, str]:
    """Return a simple business model canvas scaffold."""
    return {
        "customer_segments": target_customer,
        "value_proposition": f"Differentiated solution for {industry}",
        "channels": "Digital marketing, partnerships, webinars",
        "revenue_streams": "Subscriptions, implementation fees, premium tiers",
    }


def estimate_costs(team_size: int, infrastructure: str) -> Dict[str, int]:
    """Estimate yearly OpEx based on team size and infra stack."""
    base_salary = team_size * 90000
    infra_multiplier = 12000 if infrastructure == "cloud" else 45000
    return {
        "annual_salary": base_salary,
        "infrastructure": infra_multiplier,
        "total_estimated": base_salary + infra_multiplier,
    }


business_planning_agent = Agent(
    name="business_planning_agent",
    model="gemini-2.5-flash",
    description="Expert at helping founders create business plans and canvases",
    instruction="""You are Zeus, an expert business strategist and startup advisor.

Focus Areas:
1. Create detailed business model canvases.
2. Identify target markets and customer segments.
3. Develop value propositions.
4. Plan revenue models.

Tool Guidance:
- Use the generate_business_canvas tool to create structured plans.""",
    tools=[
        FunctionTool(generate_business_canvas),
        FunctionTool(estimate_costs),
    ],
)


__all__ = [
    "business_planning_agent",
    "generate_business_canvas",
    "estimate_costs",
]
