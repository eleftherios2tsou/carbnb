from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from uuid import UUID

class PhotoPresignOut(BaseModel):
    upload_url: HttpUrl   
    key: str             

class PhotoCreateConfirmIn(BaseModel):
    key: str
    is_cover: bool | None = None
    sort_order: int | None = Field(default=None, ge=0)

class PhotoOut(BaseModel):
    id: UUID
    car_id: UUID
    url: HttpUrl
    is_cover: bool
    sort_order: int

class CarOut(BaseModel):
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