from datetime import datetime

from pydantic import BaseModel, Field


class InventoryCreate(BaseModel):
    product_id: int = Field(ge=1)
    warehouse_id: int = Field(ge=1)
    quantity: int = Field(default=0, ge=0)
    reserved_quantity: int = Field(default=0, ge=0)
    damaged_quantity: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=0, ge=0)


class InventoryUpdate(BaseModel):
    quantity: int | None = Field(default=None, ge=0)
    reserved_quantity: int | None = Field(default=None, ge=0)
    damaged_quantity: int | None = Field(default=None, ge=0)
    reorder_level: int | None = Field(default=None, ge=0)


class InventoryAdjustment(BaseModel):
    inventory_id: int = Field(ge=1)
    amount: int
    reason: str = Field(min_length=2, max_length=255)


class InventoryResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    quantity: int
    reserved_quantity: int
    damaged_quantity: int
    reorder_level: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class InventoryTransfer(BaseModel):
    product_id: int = Field(ge=1)
    source_warehouse_id: int = Field(ge=1)
    destination_warehouse_id: int = Field(ge=1)
    quantity: int = Field(gt=0)


class InventoryTransactionResponse(BaseModel):
    id: int
    inventory_id: int
    product_id: int
    warehouse_id: int
    transaction_type: str
    quantity: int
    reference_type: str | None
    reference_id: int | None
    reason: str | None
    created_by: int | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
