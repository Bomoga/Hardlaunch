from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Literal, Optional

from google.adk.sessions.state import State
from google.adk.tools.tool_context import ToolContext

BusinessSummarySource = Literal["survey", "manual", "system"]

@dataclass
class BusinessSummaryRecord:
    summary: str
    source: BusinessSummarySource
    updated_at: str


BUSINESS_SUMMARY_KEY = f"{State.USER_PREFIX}business_summary"


def _normalize_summary(summary: str) -> str:
    normalized = summary.strip()
    if not normalized:
        raise ValueError("Business summary cannot be empty.")
    return normalized


def save_business_summary(
    summary: str,
    *,
    source: BusinessSummarySource = "survey",
    tool_context: ToolContext,
) -> dict[str, str]:
    """Persist the latest business summary in user-scoped state."""
    try:
        normalized = _normalize_summary(summary)
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}
    record = BusinessSummaryRecord(
        summary=normalized,
        source=source,
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
    tool_context.state[BUSINESS_SUMMARY_KEY] = asdict(record)
    return {
        "status": "success",
        "message": "Business summary saved for future workflows.",
    }


def get_business_summary(
    *,
    tool_context: ToolContext,
) -> dict[str, Optional[str]]:
    """Fetch the stored business summary, if any."""
    record: Optional[dict] = tool_context.state.get(BUSINESS_SUMMARY_KEY)
    if not record:
        return {"summary": None, "source": None, "updated_at": None}
    return {
        "summary": record.get("summary"),
        "source": record.get("source"),
        "updated_at": record.get("updated_at"),
    }
