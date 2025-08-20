from pydantic import BaseModel, ConfigDict
from datetime import date
from uuid import UUID

class BookingCreateIn(BaseModel):
    car_id: UUID
    start_date: date
    end_date: date

class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    car_id: UUID
    renter_id: UUID
    start_date: date
    end_date: date
    status: str
    total_price_cents: int
