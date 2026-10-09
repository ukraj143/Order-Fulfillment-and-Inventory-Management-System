from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    category_id: int = Field(..., ge=1)
    sku: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    price: Decimal = Field(..., ge=0, decimal_places=2)
    is_active: bool = True


class ProductUpdate(BaseModel):
    category_id: int | None = Field(default=None, ge=1)
    sku: str | None = Field(default=None, min_length=1, max_length=100)
    name: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    price: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    is_active: bool | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    sku: str
    name: str
    description: str | None
    price: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime