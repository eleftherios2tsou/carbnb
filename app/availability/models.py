import uuid
from datetime import date, datetime
from sqlalchemy import Date, Text, ForeignKey, CheckConstraint, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class AvailabilityBlock(Base):
    __tablename__ = "availability_blocks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    car_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cars.id", ondelete="CASCADE"), index=True)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date:   Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("start_date <= end_date", name="block_start_before_end"),
    )
