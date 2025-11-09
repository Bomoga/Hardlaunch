from __future__ import annotations

from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

from tools.context_memory_tools import BUSINESS_SUMMARY_KEY

STARTUP_KNOWLEDGE_BASE = {
    "business_model": """
    Business Model Canvas - 9 Key Components:
    1. Customer Segments: Define distinct groups of customers
    2. Value Propositions: Solve customer problems and satisfy needs
    3. Channels: Communication, distribution, and sales channels
    4. Customer Relationships: Personal assistance, self-service, automated
    5. Revenue Streams: Asset sale, subscription, licensing, advertising
    6. Key Resources: Physical, intellectual, human, financial assets
    7. Key Activities: Production, problem solving, platform maintenance
    8. Key Partnerships: Strategic alliances, supplier relationships
    9. Cost Structure: Fixed costs, variable costs, economies of scale
    
    Iterate based on customer feedback and market validation.
    """,
    
    "funding": """
    Startup Funding Stages:
    - Pre-Seed: $10k-$500k (friends/family, validate idea, build prototype)
    - Seed: $500k-$2M (angels, achieve product-market fit, equity: 10-25%)
    - Series A: $2M-$15M (VCs, scale operations, equity: 15-30%)
    - Series B: $10M-$50M (late VCs, market expansion, equity: 10-20%)
    - Series C+: $50M+ (IPO prep, acquisitions)
    
    Alternatives: Bootstrapping, revenue-based financing, crowdfunding, grants
    """,
    
    "market_sizing": """
    TAM, SAM, SOM Framework:
    - TAM (Total Addressable Market): 100% market share potential
    - SAM (Serviceable Addressable Market): Realistic reach with your channels
    - SOM (Serviceable Obtainable Market): Near-term achievable market share
    
    Example: TAM $100B → SAM $10B (region/segment) → SOM $100M (1% capture)
    Investors want: Large TAM ($1B+), focused SAM, achievable SOM
    """,
    
    "tech_stack": """
    Recommended Startup Tech Stack:
    - Frontend: Next.js + Tailwind CSS (React + SSR, modern, SEO-friendly)
    - Backend: FastAPI (Python, async, ML integration) or Next.js API routes
    - Database: PostgreSQL via Supabase (reliable, auth included)
    - Hosting: Vercel (frontend) + Supabase (backend/DB)
    - Auth: Supabase Auth or Clerk
    
    Prioritize: Speed to market > Perfect architecture. Choose proven tech.
    Other options: Vue, Django, MongoDB, Railway, AWS/GCP for scaling
    """,
    
    "gtm_strategy": """
    Go-To-Market Strategies:
    - Product-Led Growth: Free trial/freemium, self-serve (Slack, Notion)
    - Sales-Led Growth: Direct sales team, enterprise focus (Salesforce)
    - Marketing-Led Growth: Content, SEO, thought leadership (HubSpot)
    - Community-Led Growth: Build community, network effects (Discord)
    
    Channels: B2C (social ads, SEO), SMB (content, partnerships), Enterprise (direct sales)
    Launch: Beta waitlist, Product Hunt, niche communities first
    """,
    
    "pricing": """
    Pricing Strategy Frameworks:
    - Value-Based: Price based on customer value (best for SaaS)
    - Freemium: Free tier + paid upgrades (2-5% conversion typical)
    - Tiered: Good/Better/Best (most common B2B SaaS)
    - Usage-Based: Pay as you grow (AWS, Stripe, Twilio)
    
    B2B SaaS Benchmarks:
    - Starter: $29-99/mo
    - Professional: $99-299/mo
    - Enterprise: $500+ custom
    - Annual discount: 16-20%
    
    Psychology: $99 vs $100, anchor high, show value metrics
    """
}


def rag_lookup(
    question: str,
    *,
    top_k: int = 5,
    tool_context: ToolContext,
) -> dict[str, str]:
    """
    Fetch grounded evidence from startup knowledge base enriched with business context.
    Uses semantic matching to find relevant startup planning information.
    """
    summary_record = tool_context.state.get(BUSINESS_SUMMARY_KEY) or {}
    summary_text = summary_record.get("summary", "")
    
    question_lower = question.lower()
    relevant_knowledge = []
    
    if any(term in question_lower for term in ["business model", "canvas", "revenue stream", "value prop"]):
        relevant_knowledge.append(STARTUP_KNOWLEDGE_BASE["business_model"])
    
    if any(term in question_lower for term in ["funding", "investment", "raise", "investor", "series", "seed"]):
        relevant_knowledge.append(STARTUP_KNOWLEDGE_BASE["funding"])
    
    if any(term in question_lower for term in ["market", "tam", "sam", "som", "market size", "addressable"]):
        relevant_knowledge.append(STARTUP_KNOWLEDGE_BASE["market_sizing"])
    
    if any(term in question_lower for term in ["tech", "stack", "framework", "database", "hosting", "architecture"]):
        relevant_knowledge.append(STARTUP_KNOWLEDGE_BASE["tech_stack"])
    
    if any(term in question_lower for term in ["gtm", "go-to-market", "launch", "channel", "acquisition", "marketing"]):
        relevant_knowledge.append(STARTUP_KNOWLEDGE_BASE["gtm_strategy"])
    
    if any(term in question_lower for term in ["pricing", "price", "cost", "subscription", "tier", "freemium"]):
        relevant_knowledge.append(STARTUP_KNOWLEDGE_BASE["pricing"])
    
    if not relevant_knowledge:
        relevant_knowledge = list(STARTUP_KNOWLEDGE_BASE.values())[:2]
    
    knowledge_context = "\n\n".join(relevant_knowledge[:top_k])
    
    answer = f"""Based on startup planning best practices:

{knowledge_context}

Applied to your business context: {summary_text if summary_text else 'Complete the survey to get personalized guidance.'}

For the most current information and deeper insights, consider using web search or consulting with specialized agents."""
    
    return {
        "answer": answer,
        "business_context": summary_text,
        "query": question,
        "sources": f"{len(relevant_knowledge)} knowledge base articles"
    }


rag_lookup_tool = FunctionTool(rag_lookup)
