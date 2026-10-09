"""
Payment Gateway Endpoints (/api/v1/payments).
"""
from fastapi import APIRouter, Depends, status
from app.schemas.all_schemas import PaymentRequest, PaymentResponse
from app.services.payment_service import PaymentService
from app.dependencies import get_payment_service, get_current_user, require_roles
from app.models.sql_models import User

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/process", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def process_payment(
    data: PaymentRequest,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    payment = await payment_service.process_payment(data, current_user.id)
    return PaymentResponse(
        transaction_id=payment.transaction_id,
        order_id=payment.order_id,
        payment_method=payment.payment_method,
        amount=payment.amount,
        status=payment.status,
        created_at=payment.created_at
    )

@router.post("/refund/{order_id}", response_model=PaymentResponse)
async def refund_payment(
    order_id: str,
    current_user: User = Depends(require_roles(["admin", "manager"])),
    payment_service: PaymentService = Depends(get_payment_service)
):
    payment = await payment_service.refund_payment(order_id)
    return PaymentResponse(
        transaction_id=payment.transaction_id,
        order_id=payment.order_id,
        payment_method=payment.payment_method,
        amount=payment.amount,
        status=payment.status,
        created_at=payment.created_at
    )
