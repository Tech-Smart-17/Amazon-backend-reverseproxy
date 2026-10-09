"""
Invoice PDF Generation & Download Endpoints (/api/v1/invoices).
"""
import os
from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.invoice_service import InvoiceService
from app.dependencies import get_invoice_service, get_current_user
from app.models.sql_models import User, Invoice
from app.exceptions import NotFoundError

router = APIRouter(prefix="/invoices", tags=["Invoices"])

@router.post("/generate/{order_id}")
async def generate_invoice(
    order_id: str,
    current_user: User = Depends(get_current_user),
    invoice_service: InvoiceService = Depends(get_invoice_service)
):
    inv = await invoice_service.generate_invoice_for_order(order_id)
    return {"success": True, "invoice_number": inv.invoice_number, "download_url": f"/api/v1/invoices/download/{inv.id}"}

@router.get("/download/{invoice_id}")
async def download_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    inv = await db.get(Invoice, invoice_id)
    if not inv or not os.path.exists(inv.file_path):
        raise NotFoundError("Invoice file")

    return FileResponse(
        path=inv.file_path,
        media_type="application/pdf",
        filename=f"{inv.invoice_number}.pdf"
    )
