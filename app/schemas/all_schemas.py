"""
Pydantic v2 validation schemas for API requests and responses.
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# ==========================================
# 1. AUTHENTICATION & USERS
# ==========================================
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    phone_number: Optional[str] = None
    role: Optional[str] = "customer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)

class UserProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    roles: List[str] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None


# ==========================================
# 2. CATEGORY & PRODUCT
# ==========================================
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None

class CategoryResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    sku: str
    title: str
    description: Optional[str] = None
    brand: Optional[str] = None
    price: float = Field(..., gt=0)
    discount_percentage: float = Field(0.0, ge=0, le=100)
    category_id: Optional[str] = None
    stock_quantity: int = Field(0, ge=0)

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    discount_percentage: Optional[float] = None
    category_id: Optional[str] = None
    is_active: Optional[bool] = None

class ProductResponse(BaseModel):
    id: str
    sku: str
    title: str
    slug: str
    description: Optional[str] = None
    brand: Optional[str] = None
    price: float
    discount_percentage: float
    final_price: float
    category_id: Optional[str] = None
    is_active: bool
    stock_quantity: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



# ==========================================
# 3. WAREHOUSE & INVENTORY
# ==========================================
class WarehouseCreate(BaseModel):
    name: str
    code: str
    location: str
    capacity: int = 100000

class WarehouseResponse(BaseModel):
    id: str
    name: str
    code: str
    location: str
    capacity: int

    model_config = ConfigDict(from_attributes=True)


class InventoryUpdate(BaseModel):
    quantity: int = Field(..., ge=0)
    warehouse_id: Optional[str] = None
    low_stock_threshold: Optional[int] = 10

class InventoryResponse(BaseModel):
    id: str
    product_id: str
    warehouse_id: Optional[str] = None
    quantity: int
    reserved_quantity: int
    low_stock_threshold: int

    model_config = ConfigDict(from_attributes=True)



# ==========================================
# 4. CART & WISHLIST
# ==========================================
class CartItemAdd(BaseModel):
    product_id: str
    quantity: int = Field(1, ge=1)

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)

class CartResponse(BaseModel):
    user_id: str
    items: List[dict] = []
    total_amount: float = 0.0

class WishlistAdd(BaseModel):
    product_id: str


# ==========================================
# 5. ADDRESS
# ==========================================
class AddressCreate(BaseModel):
    full_name: str
    street_address: str
    city: str
    state: str
    postal_code: str
    country: str = "USA"
    phone: str
    is_default: bool = False

class AddressResponse(BaseModel):
    id: str
    user_id: str
    full_name: str
    street_address: str
    city: str
    state: str
    postal_code: str
    country: str
    phone: str
    is_default: bool

    model_config = ConfigDict(from_attributes=True)



# ==========================================
# 6. ORDERS & PAYMENTS
# ==========================================
class OrderCreate(BaseModel):
    address_id: str
    payment_method: str
    coupon_code: Optional[str] = None

class OrderItemResponse(BaseModel):
    product_id: str
    product_name: str
    unit_price: float
    quantity: int
    total_price: float

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: str
    order_number: str
    user_id: str
    address_id: Optional[str] = None
    status: str
    total_amount: float
    discount_amount: float
    final_amount: float
    created_at: datetime
    items: List[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class PaymentRequest(BaseModel):
    order_id: str
    payment_method: str
    card_number: Optional[str] = None
    upi_id: Optional[str] = None

class PaymentResponse(BaseModel):
    transaction_id: str
    order_id: str
    payment_method: str
    amount: float
    status: str
    created_at: datetime


# ==========================================
# 7. REVIEWS & NOTIFICATIONS
# ==========================================
class ReviewCreate(BaseModel):
    product_id: str
    rating: float = Field(..., ge=1.0, le=5.0)
    comment: str

class ReviewResponse(BaseModel):
    id: Optional[str] = None
    product_id: str
    user_id: str
    user_name: str
    rating: float
    comment: str
    created_at: datetime

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime


# ==========================================
# 8. ANALYTICS & SEARCH
# ==========================================
class AnalyticsDashboardResponse(BaseModel):
    total_users: int
    total_products: int
    total_orders: int
    total_revenue: float
    low_stock_products_count: int

class SearchQueryRequest(BaseModel):
    query: str
    limit: int = 10
