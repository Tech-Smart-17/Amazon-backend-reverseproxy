"""Optional PDF RAG and natural-language SQL endpoints."""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.config import settings
from app.dependencies import (
    get_current_user,
    get_knowledge_service,
    get_sql_agent_service,
    require_roles,
)
from app.models.sql_models import User
from app.schemas.ai_schemas import AIQuestion, KnowledgeAnswer, PDFIndexResult, SQLAgentAnswer
from app.services.knowledge_service import KnowledgeService
from app.services.sql_agent_service import SQLAgentService


router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/knowledge/pdfs", response_model=PDFIndexResult)
async def index_knowledge_pdf(
    file: UploadFile = File(...),
    _admin: User = Depends(require_roles(["admin"])),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
):
    """Index a PDF for grounded answers. Only administrators can add documents."""
    filename = file.filename or "uploaded.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Upload a PDF file.")
    contents = await file.read(settings.KNOWLEDGE_UPLOAD_MAX_BYTES + 1)
    if len(contents) > settings.KNOWLEDGE_UPLOAD_MAX_BYTES:
        raise HTTPException(status_code=413, detail="PDF exceeds the configured upload limit.")
    if not contents.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF.")
    try:
        return await knowledge_service.index_pdf(filename, contents)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/knowledge/ask", response_model=KnowledgeAnswer)
async def ask_knowledge_base(
    request: AIQuestion,
    _user: User = Depends(get_current_user),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
):
    """Answer from indexed PDFs and return source/page citations."""
    return await knowledge_service.answer(request.question)


@router.post("/sql/ask", response_model=SQLAgentAnswer)
async def ask_sql_agent(
    request: AIQuestion,
    _admin: User = Depends(require_roles(["admin"])),
    sql_agent: SQLAgentService = Depends(get_sql_agent_service),
):
    """Answer admin questions using a read-only agent restricted to catalog tables."""
    return {"answer": await sql_agent.answer(request.question)}
