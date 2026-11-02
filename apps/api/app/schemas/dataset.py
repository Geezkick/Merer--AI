from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DatasetCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str | None = None


class DatasetResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    description: str | None
    version: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
