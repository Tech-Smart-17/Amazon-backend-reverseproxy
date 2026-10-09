"""
Payment Gateway Integration Service (UPI, Credit Card, Debit Card, Cash On Delivery).
"""
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.order_repository import OrderRepository
from app.models.sql_models import Payment
from app.schemas.all_schemas import PaymentRequest
from app.exceptions import NotFoundError, PaymentFailedError

class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)

    async def process_payment(self, data: PaymentRequest, user_id: str) -> Payment:
        order = await self.order_repo.get_by_id(data.order_id)
        if not order or order.user_id != user_id:
            raise NotFoundError("Order")

        if order.payment:
            return order.payment

        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        payment_status = "completed"

        payment = Payment(
            order_id=order.id,
            transaction_id=transaction_id,
            payment_method=data.payment_method,
            amount=order.final_amount,
            status=payment_status
        )
        self.db.add(payment)
        
        # Advance order status to processing
        order.status = "processing"
        await self.db.flush()

        return payment

    async def refund_payment(self, order_id: str) -> Payment:
        order = await self.order_repo.get_by_id(order_id)
        if not order or not order.payment:
            raise NotFoundError("Payment record for Order")

        order.payment.status = "refunded"
        order.status = "refunded"
        await self.db.flush()
        return order.payment
