"""Request and response models for the optional AI endpoints."""
from typing import Any

from pydantic import BaseModel, Field


class AIQuestion(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


class PDFIndexResult(BaseModel):
    document_id: str
    source: str
    chunks_indexed: int


class KnowledgeAnswer(BaseModel):
    answer: str
    sources: list[dict[str, Any]]


class SQLAgentAnswer(BaseModel):
    answer: str
