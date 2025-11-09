from __future__ import annotations

from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

from rag.service import query_documents
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

    enriched_question = (
        f"Business Summary:\n{summary_text}\n\nUser Question:\n{question}"
        if summary_text
        else question
    )

    response_text = query_documents(enriched_question, top_k=top_k)
    return {"answer": response_text}


rag_lookup_tool = FunctionTool(rag_lookup)
