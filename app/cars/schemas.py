from pydantic import BaseModel, Field
from uuid import UUID

class CarIn(BaseModel):
    make: str
    model: str
    year: int = Field(ge=1980)
    seats: int = Field(ge=1)
    transmission: str  # 'manual' or 'automatic'
    fuel: str | None = None
    description: str | None = None
    daily_price_cents: int = Field(gt=0)
    location_text: str
    lat: float | None = None
    lng: float | None = None

class CarOut(BaseModel):
    id: UUID
    owner_id: UUID
    make: str
    model: str
    year: int
    seats: int
    transmission: str
    fuel: str | None = None
    description: str | None = None
    daily_price_cents: int
    location_text: str
    lat: float | None = None
    lng: float | None = None
    is_active: bool
