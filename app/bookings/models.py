import uuid
from datetime import date, datetime
from sqlalchemy import (
    String, Enum, ForeignKey, CheckConstraint, Date, Integer, DateTime, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

BOOKING_STATUS = ("pending", "confirmed", "cancelled", "completed")

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    car_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cars.id", ondelete="CASCADE"), index=True)
    renter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date:   Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[str] = mapped_column(Enum(*BOOKING_STATUS, name="booking_status"), default="pending", nullable=False)

    total_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("start_date <= end_date", name="booking_start_before_end"),
        CheckConstraint("total_price_cents > 0", name="booking_price_positive"),
    )
