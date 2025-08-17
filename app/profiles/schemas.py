from pydantic import BaseModel, Field

class ProfileOut(BaseModel):
    full_name: str
    phone: str | None = None
    about: str | None = None
    driver_license_number: str | None = None
    driver_license_photo_url: str | None = None
    verified: bool = False

class ProfileUpsertIn(BaseModel):
    full_name: str = Field(min_length=1)
    phone: str | None = None
    about: str | None = None
    driver_license_number: str | None = None
    driver_license_photo_url: str | None = None
