"""
PDF Invoice Generation & File Management Service.
"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.order_repository import OrderRepository
from app.models.sql_models import Invoice
from app.utils import create_pdf_invoice
from app.exceptions import NotFoundError

class InvoiceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)

    async def generate_invoice_for_order(self, order_id: str) -> Invoice:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundError("Order")

        if order.invoice:
            return order.invoice

        invoice_num = f"INV-{order.order_number}"
        order_data = {
            "order_id": order.order_number,
            "payment_method": order.payment.payment_method if order.payment else "COD",
            "total_amount": order.final_amount,
            "items": [
                {
                    "title": item.product_name,
                    "quantity": item.quantity,
                    "price": item.unit_price
                } for item in order.items
            ]
        }

        pdf_path = create_pdf_invoice(invoice_num, order_data)

        invoice = Invoice(
            invoice_number=invoice_num,
            order_id=order.id,
            file_path=pdf_path
        )
        self.db.add(invoice)
        await self.db.flush()

        return invoice
