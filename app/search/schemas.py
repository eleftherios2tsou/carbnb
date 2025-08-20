from pydantic import BaseModel, ConfigDict, HttpUrl
from uuid import UUID

class SearchCarOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    distance_km: float | None = None
