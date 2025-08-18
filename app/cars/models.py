import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, CheckConstraint, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class Car(Base):
    __tablename__ = "cars"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)

    make: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    seats: Mapped[int] = mapped_column(Integer, nullable=False)

    transmission: Mapped[str] = mapped_column(String, nullable=False)  # 'manual' or 'automatic'
    fuel: Mapped[str | None] = mapped_column(String, nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    daily_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)

    location_text: Mapped[str] = mapped_column(String, nullable=False)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("year BETWEEN 1980 AND EXTRACT(YEAR FROM now())::int + 1", name="car_year_valid"),
        CheckConstraint("seats > 0", name="car_seats_positive"),
        CheckConstraint("daily_price_cents > 0", name="car_price_positive"),
        CheckConstraint("transmission IN ('manual','automatic')", name="car_transmission_valid"),
    )
