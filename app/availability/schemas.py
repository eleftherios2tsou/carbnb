from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from uuid import UUID

class BlockIn(BaseModel):
    start_date: date
    end_date: date
    reason: str | None = Field(default=None, max_length=500)

class BlockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    car_id: UUID
    start_date: date
    end_date: date
    reason: str | None = None
