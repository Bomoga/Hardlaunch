from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Sequence

from dotenv import load_dotenv
from llama_index.core import (
    Document,
    Settings,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.embeddings.google import GoogleGenAIEmbedding
from llama_index.llms.gemini import Gemini


# --- Environment & model configuration ---------------------------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing. Add it to .env or the environment.")

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "models/embedding-001")

Settings.llm = Gemini(model=MODEL_NAME, api_key=GEMINI_API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name=EMBED_MODEL_NAME, api_key=GEMINI_API_KEY)

BASE_DIR = Path(__file__).resolve().parents[1] / "data"
PERSIST_DIR = BASE_DIR / "persist"
TRANSCRIPT_DIR = PERSIST_DIR / "transcript"
WEBPAGE_DIR = BASE_DIR / "webpages"

for path in (BASE_DIR, PERSIST_DIR, TRANSCRIPT_DIR, WEBPAGE_DIR):
    path.mkdir(parents=True, exist_ok=True)


# --- Internal helpers --------------------------------------------------------

def _index_exists() -> bool:
    return PERSIST_DIR.exists() and any(PERSIST_DIR.iterdir())


def _load_index() -> VectorStoreIndex:
    storage_context = StorageContext.from_defaults(persist_dir=str(PERSIST_DIR))
    return load_index_from_storage(storage_context)


def _persist(index: VectorStoreIndex) -> None:
    index.storage_context.persist(persist_dir=str(PERSIST_DIR))


# --- Public ingestion API ----------------------------------------------------

def rebuild_index(documents: Sequence[Document]) -> None:
    """Create a fresh index from the provided documents."""
    docs = list(documents)
    if not docs:
        raise ValueError("rebuild_index requires at least one document.")
    index = VectorStoreIndex.from_documents(docs)
    _persist(index)


def upsert_documents(documents: Iterable[Document]) -> None:
    """Insert new documents into the existing index, or create one if absent."""
    docs = list(documents)
    if not docs:
        return
    try:
        index = _load_index()
    except Exception:
        index = VectorStoreIndex.from_documents(docs)
    else:
        for doc in docs:
            index.insert(doc)
    _persist(index)


# --- Retrieval utilities -----------------------------------------------------

def get_query_engine(top_k: int = 5):
    """Return a LlamaIndex query engine backed by the persisted store."""
    if not _index_exists():
        raise RuntimeError("No persisted index found; ingest documents first.")
    index = _load_index()
    return index.as_query_engine(similarity_top_k=top_k)


def query_documents(question: str, *, top_k: int = 5) -> str:
    """Run a semantic RAG query and return the model's answer as text."""
    engine = get_query_engine(top_k=top_k)
    response = engine.query(question)
    return str(response)


def retrieve_evidence(
    questions: Sequence[str],
    *,
    top_k: int = 5,
) -> dict[str, str]:
    """
    Convenience helper for agents: ask multiple focused questions
    and receive a dict mapping each prompt to its textual answer.
    """
    engine = get_query_engine(top_k=top_k)
    answers: dict[str, str] = {}
    for q in questions:
        answers[q] = str(engine.query(q))
    return answers