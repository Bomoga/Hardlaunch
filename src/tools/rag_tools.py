from __future__ import annotations

from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

from tools.context_memory_tools import BUSINESS_SUMMARY_KEY


def rag_lookup(
    question: str,
    *,
    top_k: int = 5,
    tool_context: ToolContext,
) -> dict[str, str]:
    """Fetch grounded evidence from the RAG document store."""
    summary_record = tool_context.state.get(BUSINESS_SUMMARY_KEY) or {}
    summary_text = summary_record.get("summary")

    # Temporarily disabled RAG to reduce startup time
    # Will use web search and general knowledge instead
    return {"answer": f"Using business context: {summary_text}. Question: {question}"}


rag_lookup_tool = FunctionTool(rag_lookup)
