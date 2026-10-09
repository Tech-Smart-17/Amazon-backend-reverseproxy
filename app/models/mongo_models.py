"""
Pydantic document schemas for MongoDB stored entities.
"""
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class CartItemDoc(BaseModel):
    product_id: str
    quantity: int = 1
    price: float
    title: str

class CartDoc(BaseModel):
    user_id: str
    items: List[CartItemDoc] = []
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WishlistItemDoc(BaseModel):
    product_id: str
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WishlistDoc(BaseModel):
    user_id: str
    items: List[WishlistItemDoc] = []

class ReviewDoc(BaseModel):
    product_id: str
    user_id: str
    user_name: str
    rating: float = Field(..., ge=1.0, le=5.0)
    comment: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NotificationDoc(BaseModel):
    user_id: str
    title: str
    message: str
    type: str = "system"
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SearchHistoryDoc(BaseModel):
    user_id: str
    query: str
    searched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserActivityDoc(BaseModel):
    user_id: str
    action: str
    details: dict = {}
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RecentlyViewedDoc(BaseModel):
    user_id: str
    product_ids: List[str] = []
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
