
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.order_item import OrderItemCreate, OrderItemResponse


class OrderCreate(BaseModel):
    customer_id: int | None = Field(default=None, ge=1)
    warehouse_id: int = Field(..., ge=1)
    shipping_address: str = Field(..., min_length=5, max_length=500)
    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., min_length=2, max_length=30)


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    customer_id: int
    created_by: int
    status: str
    total_amount: Decimal
    shipping_address: str
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = []

