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
    Fetch grounded evidence from combined knowledge sources:
    1. In-memory startup fundamentals (business models, funding, pricing, etc.)
    2. LlamaIndex vector store (Growth Hacking documents)
    
    Enriched with user's business context for personalized guidance.
    """
    summary_record = tool_context.state.get(BUSINESS_SUMMARY_KEY) or {}
    summary_text = summary_record.get("summary", "")
    
    question_lower = question.lower()
    relevant_knowledge = []
    sources = []
    
    # Part 1: In-memory startup fundamentals
    if any(term in question_lower for term in ["business model", "canvas", "revenue stream", "value prop"]):
        relevant_knowledge.append(STARTUP_KNOWLEDGE_BASE["business_model"])
        sources.append("Business Model Canvas")
    
    if any(term in question_lower for term in ["funding", "investment", "raise", "investor", "series", "seed"]):
        relevant_knowledge.append(STARTUP_KNOWLEDGE_BASE["funding"])
        sources.append("Funding Stages")
    
    if any(term in question_lower for term in ["market", "tam", "sam", "som", "market size", "addressable"]):
        relevant_knowledge.append(STARTUP_KNOWLEDGE_BASE["market_sizing"])
        sources.append("Market Sizing Framework")
    
    if any(term in question_lower for term in ["tech", "stack", "framework", "database", "hosting", "architecture"]):
        relevant_knowledge.append(STARTUP_KNOWLEDGE_BASE["tech_stack"])
        sources.append("Tech Stack Guide")
    
    if any(term in question_lower for term in ["gtm", "go-to-market", "launch", "channel", "acquisition", "marketing"]):
        relevant_knowledge.append(STARTUP_KNOWLEDGE_BASE["gtm_strategy"])
        sources.append("GTM Strategy")
    
    if any(term in question_lower for term in ["pricing", "price", "cost", "subscription", "tier", "freemium"]):
        relevant_knowledge.append(STARTUP_KNOWLEDGE_BASE["pricing"])
        sources.append("Pricing Strategy")
    
    # Part 2: Query LlamaIndex vector store for Growth Hacking insights
    vector_store_results = ""
    try:
        from rag.service import query_documents
        
        enriched_question = question
        if summary_text:
            enriched_question = f"Given this business context: {summary_text}\n\nQuestion: {question}"
        
        vector_store_results = query_documents(enriched_question, top_k=3)
        sources.append("Hacking Growth (vector store)")
        
    except Exception as e:
        vector_store_results = ""
    
    # Combine all knowledge sources
    knowledge_parts = []
    
    if relevant_knowledge:
        knowledge_parts.append("**Startup Fundamentals:**\n" + "\n\n".join(relevant_knowledge[:2]))
    
    if vector_store_results:
        knowledge_parts.append(f"**Growth Hacking Insights:**\n{vector_store_results}")
    
    if not knowledge_parts:
        relevant_knowledge = list(STARTUP_KNOWLEDGE_BASE.values())[:2]
        knowledge_parts.append("**General Startup Guidance:**\n" + "\n\n".join(relevant_knowledge))
        sources.append("Startup Knowledge Base")
    
    combined_knowledge = "\n\n---\n\n".join(knowledge_parts)
    
    answer = f"""Based on multiple authoritative sources:

{combined_knowledge}

**Applied to Your Business:**
{summary_text if summary_text else 'Complete the survey to get personalized guidance tailored to your specific startup.'}

**Recommendations:**
- Use the specialized agents (Business Planning, Financial Research, Market Analytics, Engineering) for deeper domain-specific guidance
- Consider web search for the most current market data and trends"""
    
    return {
        "answer": answer,
        "business_context": summary_text,
        "query": question,
        "sources": ", ".join(sources) if sources else "Knowledge base"
    }


rag_lookup_tool = FunctionTool(rag_lookup)
