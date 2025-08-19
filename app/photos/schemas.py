from pydantic import BaseModel, Field, HttpUrl
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
