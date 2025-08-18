from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.db import get_db
from app.deps import get_current_user
from app.cars.models import Car
from app.cars.schemas import CarIn, CarOut, CarUpdate
from sqlalchemy.exc import DataError, IntegrityError

router = APIRouter(prefix="/cars", tags=["cars"])

@router.post("", response_model=CarOut)
def create_car(body: CarIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    car = Car(owner_id=user.id, **body.model_dump())
    db.add(car)
    db.commit()
    db.refresh(car)
    return car

@router.get("/{car_id}", response_model=CarOut)
def get_car(car_id: UUID, db: Session = Depends(get_db)):
    car = db.get(Car, car_id)
    if not car or not car.is_active:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

@router.get("", response_model=list[CarOut])
def list_my_cars(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Car).filter(Car.owner_id == user.id).order_by(Car.created_at.desc()).all()


def _get_owned_car_or_404(car_id: UUID, db: Session, user_id: UUID) -> Car:
    car = db.get(Car, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    if car.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not your car")
    return car

@router.patch("/{car_id}", response_model=CarOut)
def update_car(
    car_id: UUID,
    body: CarUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    car = _get_owned_car_or_404(car_id, db, user.id)

    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(car, k, v)

    try:
        db.add(car)
        db.commit()
    except (IntegrityError, DataError) as e:
        db.rollback()
        # Friendly messages for common constraints
        msg = str(e.orig)
        if "car_transmission_valid" in msg:
            raise HTTPException(status_code=400, detail="transmission must be 'manual' or 'automatic'")
        if "car_seats_positive" in msg:
            raise HTTPException(status_code=400, detail="seats must be > 0")
        if "car_price_positive" in msg:
            raise HTTPException(status_code=400, detail="daily_price_cents must be > 0")
        if "car_year_valid" in msg:
            raise HTTPException(status_code=400, detail="year is out of allowed range")
        raise HTTPException(status_code=400, detail="invalid data for car update")
    db.refresh(car)
    return car