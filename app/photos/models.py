import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class CarPhoto(Base):
    __tablename__ = "car_photos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    car_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cars.id", ondelete="CASCADE"), index=True)

    s3_key: Mapped[str] = mapped_column(String, nullable=False)     
    url: Mapped[str] = mapped_column(Text, nullable=False)          

    is_cover: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
