from pydantic import BaseModel, Field, field_validator, ConfigDict, HttpUrl
from uuid import UUID
from datetime import datetime

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
    cover_photo_url: HttpUrl | None = None

class CarUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

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

    @field_validator("make", "model", "fuel", "location_text", mode="before")
    @classmethod
    def check_year(cls, v):
        if v is None:
            return v
        max_year = datetime.now().year + 1
        if v > max_year:
            raise ValueError(f"year must be <= {max_year}")
        return v

    @field_validator("lat")
    @classmethod
    def check_lat(cls, v):
        if v is None:
            return v
        if not (-90.0 <= v <= 90.0):
            raise ValueError("lat must be between -90 and 90")
        return v