from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, not_
from uuid import UUID
from datetime import date

from app.db import get_db
from app.deps import get_current_user
from app.cars.models import Car
from app.availability.models import AvailabilityBlock
from app.availability.schemas import BlockIn, BlockOut

router = APIRouter(prefix="/cars", tags=["availability"])

def _owned_car(db: Session, car_id: UUID, user_id: UUID) -> Car:
    car = db.get(Car, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    if car.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not your car")
    return car

def _has_overlap(db: Session, car_id: UUID, start: date, end: date, exclude_id: UUID | None = None) -> bool:
    q = db.query(AvailabilityBlock).filter(AvailabilityBlock.car_id == car_id)
    if exclude_id:
        q = q.filter(AvailabilityBlock.id != exclude_id)
    q = q.filter(
        not_(
            (AvailabilityBlock.end_date < start) |
            (AvailabilityBlock.start_date > end)
        )
    )
    return db.query(q.exists()).scalar()

@router.get("/{car_id}/availability-blocks", response_model=list[BlockOut])
def list_blocks(car_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    _owned_car(db, car_id, user.id)
    return (
        db.query(AvailabilityBlock)
        .filter(AvailabilityBlock.car_id == car_id)
        .order_by(AvailabilityBlock.start_date.asc())
        .all()
    )

@router.post("/{car_id}/availability-blocks", response_model=BlockOut, status_code=status.HTTP_201_CREATED)
def create_block(car_id: UUID, body: BlockIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    _owned_car(db, car_id, user.id)
    if body.end_date < body.start_date:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date")
    if _has_overlap(db, car_id, body.start_date, body.end_date):
        raise HTTPException(status_code=400, detail="date range overlaps an existing block")
    block = AvailabilityBlock(car_id=car_id, **body.model_dump())
    db.add(block)
    db.commit()
    db.refresh(block)
    return block

@router.delete("/{car_id}/availability-blocks/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_block(car_id: UUID, block_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    _owned_car(db, car_id, user.id)
    block = db.get(AvailabilityBlock, block_id)
    if not block or block.car_id != car_id:
        raise HTTPException(status_code=404, detail="Block not found")
    db.delete(block)
    db.commit()
