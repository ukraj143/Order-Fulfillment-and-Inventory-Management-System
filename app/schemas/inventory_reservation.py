from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InventoryReservationCreate(BaseModel):
    product_id: int = Field(..., ge=1)
    warehouse_id: int = Field(..., ge=1)
    order_id: int = Field(..., ge=1)
    quantity: int = Field(..., gt=0)


class InventoryReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    warehouse_id: int
    order_id: int
    quantity: int
    status: str
    created_at: datetime
    released_at: datetime | None