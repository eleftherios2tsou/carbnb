from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.db import get_db
from app.deps import get_current_user
from app.cars.models import Car
from app.cars.schemas import CarIn, CarOut

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
