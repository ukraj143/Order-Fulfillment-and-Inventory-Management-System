from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuditLogCreate(BaseModel):
    user_id: int | None = Field(default=None, ge=1)
    action: str = Field(..., min_length=2, max_length=100)
    entity_type: str = Field(..., min_length=2, max_length=100)
    entity_id: str | None = Field(default=None, max_length=100)
    description: str | None = None


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    action: str
    entity_type: str
    entity_id: str | None
    description: str | None
    created_at: datetime