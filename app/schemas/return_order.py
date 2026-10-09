from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReturnCreate(BaseModel):
    order_id: int = Field(..., ge=1)
    reason: str = Field(..., min_length=5, max_length=500)
    quantity: int = Field(..., gt=0)


class ReturnStatusUpdate(BaseModel):
    status: str = Field(..., min_length=2, max_length=30)


class ReturnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    reason: str
    quantity: int
    status: str
    created_at: datetime
    processed_at: datetime | None