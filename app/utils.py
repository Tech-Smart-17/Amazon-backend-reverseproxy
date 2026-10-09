"""
Utility functions for file handling and PDF invoice generation.
"""
import os
import uuid
from typing import Dict, Any
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from app.config import settings

def save_uploaded_file(file_bytes: bytes, filename: str, subfolder: str = "product_images") -> str:
    """Save file to local uploads directory and return relative path."""
    ext = filename.split(".")[-1] if "." in filename else "jpg"
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    target_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, unique_name)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    return f"/static/{subfolder}/{unique_name}"

def create_pdf_invoice(invoice_number: str, order_data: Dict[str, Any]) -> str:
    """Generate a styled PDF Invoice and return the file path."""
    file_path = os.path.join(settings.INVOICE_DIR, f"{invoice_number}.pdf")
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#FF9900"),
        spaceAfter=12
    )
    story.append(Paragraph("AMAZON STORE - OFFICIAL INVOICE", title_style))
    story.append(Spacer(1, 10))

    meta_text = f"<b>Invoice Number:</b> {invoice_number}<br/>" \
                f"<b>Order ID:</b> {order_data.get('order_id', 'N/A')}<br/>" \
                f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>" \
                f"<b>Payment Method:</b> {order_data.get('payment_method', 'CARD')}"
    story.append(Paragraph(meta_text, styles['Normal']))
    story.append(Spacer(1, 15))

    # Items table
    data = [["Item Description", "Qty", "Price", "Total"]]
    items = order_data.get('items', [])
    for item in items:
        price = float(item.get('price', 0.0))
        qty = int(item.get('quantity', 1))
        tot = price * qty
        data.append([item.get('title', 'Product'), str(qty), f"${price:.2f}", f"${tot:.2f}"])

    data.append(["", "", "<b>Grand Total:</b>", f"<b>${order_data.get('total_amount', 0.0):.2f}</b>"])

    table = Table(data, colWidths=[240, 60, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#232F3E")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.whitesmoke)
    ]))
    story.append(table)

    doc.build(story)
    return file_path
