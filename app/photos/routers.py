from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from app.db import get_db
from app.deps import get_current_user
from app.cars.models import Car
from app.photos.models import CarPhoto
from app.photos.schemas import PhotoPresignOut, PhotoCreateConfirmIn, PhotoOut
from app.photos.s3 import make_car_photo_key, presign_put_url, public_url, delete_object
from fastapi import status
from sqlalchemy import and_

router = APIRouter(prefix="/cars", tags=["photos"])

def _owned_car(db: Session, car_id: UUID, user_id: UUID) -> Car:
    car = db.get(Car, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    if car.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not your car")
    return car

@router.post("/{car_id}/photos/presign", response_model=PhotoPresignOut)
def presign_upload(
    car_id: UUID,
    content_type: str = Query("image/jpeg"),
    ext: str = Query("jpg"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    _owned_car(db, car_id, user.id)
    key = make_car_photo_key(str(car_id), ext=ext)
    url = presign_put_url(key, content_type=content_type)
    return PhotoPresignOut(upload_url=url, key=key)

@router.post("/{car_id}/photos", response_model=PhotoOut)
def confirm_photo(
    car_id: UUID,
    body: PhotoCreateConfirmIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    _owned_car(db, car_id, user.id)
    photo = CarPhoto(
        car_id=car_id,
        s3_key=body.key,
        url=public_url(body.key),
        is_cover=bool(body.is_cover) if body.is_cover is not None else False,
        sort_order=body.sort_order or 0,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo

@router.get("/{car_id}/photos", response_model=list[PhotoOut])
def list_photos(
    car_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    _owned_car(db, car_id, user.id)
    return db.query(CarPhoto).filter(CarPhoto.car_id == car_id).order_by(CarPhoto.sort_order.asc(), CarPhoto.created_at.asc()).all()


@router.patch("/{car_id}/photos/{photo_id}", response_model=PhotoOut)
def update_photo(
    car_id: UUID,
    photo_id: UUID,
    is_cover: bool | None = None,
    sort_order: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    _owned_car(db, car_id, user.id)
    photo = db.get(CarPhoto, photo_id)
    if not photo or photo.car_id != car_id:
        raise HTTPException(status_code=404, detail="Photo not found")

    if sort_order is not None:
        if sort_order < 0:
            raise HTTPException(status_code=400, detail="sort_order must be >= 0")
        photo.sort_order = sort_order

    if is_cover is not None:
        photo.is_cover = is_cover
        if is_cover:
            db.query(CarPhoto).filter(
                and_(CarPhoto.car_id == car_id, CarPhoto.id != photo_id)
            ).update({CarPhoto.is_cover: False})

    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


@router.delete("/{car_id}/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    car_id: UUID,
    photo_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    _owned_car(db, car_id, user.id)
    photo = db.get(CarPhoto, photo_id)
    if not photo or photo.car_id != car_id:
        raise HTTPException(status_code=404, detail="Photo not found")

    try:
        delete_object(photo.s3_key)
    except Exception:
        pass

    db.delete(photo)
    db.commit()
