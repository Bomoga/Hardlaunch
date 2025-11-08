from __future__ import annotations

from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

from rag.service import query_documents
from tools.context_memory_tools import BUSINESS_SUMMARY_KEY


def _rag_lookup(
    question: str,
    *,
    top_k: int = 5,
    tool_context: ToolContext,
) -> dict[str, str]:
    """
    Retrieve grounded evidence from the RAG document store.

    The current business summary (if any) is prepended so the retriever can
    align results with the user’s latest context.
    """
    summary_record = tool_context.state.get(BUSINESS_SUMMARY_KEY) or {}
    summary_text = summary_record.get("summary")

    enriched_question = (
        f"Business Summary:\n{summary_text}\n\nUser Question:\n{question}"
        if summary_text
        else question
    )

    response_text = query_documents(enriched_question, top_k=top_k)
    return {"answer": response_text}


rag_lookup_tool = FunctionTool(
    name="rag_lookup",
    description=(
        "Search the uploaded RAG documents for concrete facts, numbers, and "
        "quotes that support the business summary or plan."
    ),
    func=_rag_lookup,
)