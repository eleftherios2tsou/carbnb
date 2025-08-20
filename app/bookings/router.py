from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, not_, exists
from uuid import UUID
from datetime import date

from app.db import get_db
from app.deps import get_current_user
from app.cars.models import Car
from app.availability.models import AvailabilityBlock
from app.bookings.models import Booking
from app.bookings.schemas import BookingCreateIn, BookingOut

router = APIRouter(prefix="/bookings", tags=["bookings"])


def _has_block_overlap(db: Session, car_id: UUID, start: date, end: date) -> bool:
    ab = exists().where(
        and_(
            AvailabilityBlock.car_id == car_id,
            not_(
                (AvailabilityBlock.end_date < start) |
                (AvailabilityBlock.start_date > end)
            ),
        )
    )
    return db.query(ab).scalar()

def _has_booking_overlap(db: Session, car_id: UUID, start: date, end: date) -> bool:
    bk = exists().where(
        and_(
            Booking.car_id == car_id,
            Booking.status.in_(("pending", "confirmed")),
            not_(
                (Booking.end_date < start) |
                (Booking.start_date > end)
            ),
        )
    )
    return db.query(bk).scalar()

def _days_inclusive(start: date, end: date) -> int:
    return (end - start).days + 1


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(body: BookingCreateIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    car = db.get(Car, body.car_id)
    if not car or not car.is_active:
        raise HTTPException(status_code=404, detail="Car not found or inactive")

    if car.owner_id == user.id:
        raise HTTPException(status_code=400, detail="Owners cannot book their own cars")

    if body.end_date < body.start_date:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date")

    with db.begin():
        if _has_block_overlap(db, car.id, body.start_date, body.end_date):
            raise HTTPException(status_code=400, detail="Dates conflict with an owner block")

        if _has_booking_overlap(db, car.id, body.start_date, body.end_date):
            raise HTTPException(status_code=400, detail="Dates conflict with another booking")

        days = _days_inclusive(body.start_date, body.end_date)
        total = days * car.daily_price_cents

        booking = Booking(
            car_id=car.id,
            renter_id=user.id,
            start_date=body.start_date,
            end_date=body.end_date,
            status="pending",
            total_price_cents=total,
        )
        db.add(booking)

    db.refresh(booking)
    return booking

@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    b = db.get(Booking, booking_id)
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")

    car = db.get(Car, b.car_id)
    if not (b.renter_id == user.id or car.owner_id == user.id):
        raise HTTPException(status_code=403, detail="Not allowed")
    return b

@router.get("/mine", response_model=list[BookingOut])
def list_my_bookings(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return (
        db.query(Booking)
        .filter(Booking.renter_id == user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )

@router.get("/owned", response_model=list[BookingOut])
def list_owned_bookings(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return (
        db.query(Booking)
        .join(Car, Car.id == Booking.car_id)
        .filter(Car.owner_id == user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )

@router.post("/{booking_id}/confirm", response_model=BookingOut)
def owner_confirm_booking(booking_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    car = db.get(Car, booking.car_id)
    if car.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the owner can confirm")
    if booking.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending bookings can be confirmed")

    if _has_block_overlap(db, booking.car_id, booking.start_date, booking.end_date):
        raise HTTPException(status_code=400, detail="Dates now conflict with an owner block")
    if _has_booking_overlap(db, booking.car_id, booking.start_date, booking.end_date):
        raise HTTPException(status_code=400, detail="Dates now conflict with another booking")

    booking.status = "confirmed"
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@router.post("/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(booking_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    car = db.get(Car, booking.car_id)
    is_renter = booking.renter_id == user.id
    is_owner = car.owner_id == user.id


    if is_renter and booking.status == "pending":
        booking.status = "cancelled"
    elif is_owner and booking.status in ("pending", "confirmed"):
        booking.status = "cancelled"
    else:
        raise HTTPException(status_code=403, detail="Not allowed to cancel this booking")

    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking
