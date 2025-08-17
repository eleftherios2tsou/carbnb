from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr