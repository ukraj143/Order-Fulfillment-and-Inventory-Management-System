from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FulfillmentCreate(BaseModel):
    order_id: int = Field(..., ge=1)
    warehouse_id: int = Field(..., ge=1)


class FulfillmentUpdate(BaseModel):
    status: str | None = Field(default=None, min_length=2, max_length=30)
    tracking_number: str | None = Field(default=None, max_length=100)
    assigned_agent_id: int | None = Field(default=None, ge=1)


class FulfillmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    warehouse_id: int
    assigned_agent_id: int | None
    status: str
    tracking_number: str | None
    shipped_at: datetime | None
    delivered_at: datetime | None
    created_at: datetime
