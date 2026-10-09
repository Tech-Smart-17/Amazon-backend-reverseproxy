"""Lazy, shared LangChain model, embedding, and vector-store factories."""
from functools import lru_cache
import os

from app.config import settings


@lru_cache(maxsize=1)
def get_embeddings():
    """Return the configured local Hugging Face embedding model."""
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(
        model_name=settings.LANGCHAIN_EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )


@lru_cache(maxsize=1)
def get_chat_model():
    """Create the configured LangChain chat model on first use."""
    from langchain.chat_models import init_chat_model

    if settings.GOOGLE_API_KEY:
        os.environ.setdefault("GOOGLE_API_KEY", settings.GOOGLE_API_KEY)
    return init_chat_model(settings.LANGCHAIN_CHAT_MODEL, temperature=0)


@lru_cache(maxsize=4)
def get_vector_store(collection_name: str):
    """Open a persistent Chroma collection using the shared embeddings."""
    from langchain_chroma import Chroma

    return Chroma(
        collection_name=collection_name,
        persist_directory=settings.CHROMADB_DIR,
        embedding_function=get_embeddings(),
        collection_metadata={"hnsw:space": "cosine"},
    )


def message_text(message) -> str:
    """Normalize LangChain text or text-content blocks to a plain string."""
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type", "text") == "text"
        ).strip()
    return str(content).strip()
