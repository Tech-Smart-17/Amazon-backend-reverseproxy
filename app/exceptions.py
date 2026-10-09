"""
Custom exception definitions and global exception handlers.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, code: str = "BAD_REQUEST"):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)

class NotFoundError(AppException):
    def __init__(self, item: str = "Item"):
        super().__init__(f"{item} not found", status_code=status.HTTP_404_NOT_FOUND, code="NOT_FOUND")

class UnauthorizedError(AppException):
    def __init__(self, message: str = "Invalid credentials or token"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED, code="UNAUTHORIZED")

class ForbiddenError(AppException):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN, code="FORBIDDEN")

class BadRequestError(AppException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST, code="BAD_REQUEST")

class InsufficientStockError(AppException):
    def __init__(self, product_name: str = "Product"):
        super().__init__(f"Insufficient stock for {product_name}", status_code=status.HTTP_400_BAD_REQUEST, code="INSUFFICIENT_STOCK")

class PaymentFailedError(AppException):
    def __init__(self, message: str = "Payment processing failed"):
        super().__init__(message, status_code=status.HTTP_402_PAYMENT_REQUIRED, code="PAYMENT_FAILED")

async def app_exception_handler(request: Request, exc: AppException):
    """Global handler for custom AppException."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Global fallback handler for unhandled internal errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc) if exc else "An unexpected error occurred."
            }
        }
    )
