from pydantic import BaseModel, Field, field_validator
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

class CarUpdate(BaseModel):
    make: str | None = None
    model: str | None = None
    year: int | None = Field(default=None, ge=1980)
    seats: int | None = Field(default=None, ge=1)
    transmission: str | None = None       # must be 'manual' or 'automatic' if present
    fuel: str | None = None
    description: str | None = None
    daily_price_cents: int | None = Field(default=None, gt=0)
    location_text: str | None = None
    lat: float | None = None
    lng: float | None = None
    is_active: bool | None = None

    @field_validator("transmission")
    @classmethod
    def check_transmission(cls, v):
        if v is None:
            return v
        if v not in {"manual", "automatic"}:
            raise ValueError("transmission must be 'manual' or 'automatic'")
        return v
