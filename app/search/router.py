from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, not_, exists, func
from math import radians, cos, sin, asin, sqrt
from typing import Optional

from app.db import get_db
from app.cars.models import Car
from app.photos.models import CarPhoto
from app.availability.models import AvailabilityBlock
from app.search.schemas import SearchCarOut

router = APIRouter(tags=["search"])


def _deg_box(lat: float, lng: float, radius_km: float) -> tuple[float, float, float, float]:
    """Return (min_lat, max_lat, min_lng, max_lng) rough box for given radius."""
    lat_delta = radius_km / 111.0
    lng_delta = radius_km / (111.0 * max(cos(radians(lat)), 1e-6))
    return (lat - lat_delta, lat + lat_delta, lng - lng_delta, lng + lng_delta)

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def _cover_url(db: Session, car_id):
    cover = (
        db.query(CarPhoto)
        .filter(CarPhoto.car_id == car_id, CarPhoto.is_cover.is_(True))
        .order_by(CarPhoto.sort_order.asc(), CarPhoto.created_at.asc())
        .first()
    )
    return cover.url if cover else None


@router.get("/search", response_model=list[SearchCarOut])
def search_cars(
    db: Session = Depends(get_db),
    lat: Optional[float] = Query(None, description="center latitude"),
    lng: Optional[float] = Query(None, description="center longitude"),
    radius_km: float = Query(25.0, gt=0, description="search radius in km (used if lat,lng provided)"),

    start: Optional[str] = Query(None, description="YYYY-MM-DD start date"),
    end: Optional[str] = Query(None, description="YYYY-MM-DD end date"),

    min_price: Optional[int] = Query(None, ge=1),
    max_price: Optional[int] = Query(None, ge=1),
    seats: Optional[int] = Query(None, ge=1),
    transmission: Optional[str] = Query(None, pattern="^(manual|automatic)$"),

    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Returns active cars matching filters and *not* blocked during [start,end].
    If lat/lng provided, sorted by distance_km (approx box + exact haversine).
    """

    q = db.query(Car).filter(Car.is_active.is_(True))

    if min_price is not None:
        q = q.filter(Car.daily_price_cents >= min_price)
    if max_price is not None:
        q = q.filter(Car.daily_price_cents <= max_price)

    if seats is not None:
        q = q.filter(Car.seats >= seats)

    
    if transmission is not None:
        q = q.filter(Car.transmission == transmission)

    if lat is not None and lng is not None:
        q = q.filter(Car.lat.isnot(None), Car.lng.isnot(None))
        min_lat, max_lat, min_lng, max_lng = _deg_box(lat, lng, radius_km)
        q = q.filter(
            Car.lat.between(min_lat, max_lat),
            Car.lng.between(min_lng, max_lng),
        )

   
    if start and end:

        start_date = func.to_date(start, "YYYY-MM-DD")
        end_date = func.to_date(end, "YYYY-MM-DD")

        ab = exists().where(
            and_(
                AvailabilityBlock.car_id == Car.id,
                not_(
                    (AvailabilityBlock.end_date < start_date)
                    | (AvailabilityBlock.start_date > end_date)
                ),
            )
        )
        q = q.filter(~ab)

    cars = q.limit(limit * 3).offset(offset).all()  

    results = []
    for c in cars:
        item = SearchCarOut.model_validate(c).model_dump()
        item["cover_photo_url"] = _cover_url(db, c.id)

        if lat is not None and lng is not None and c.lat is not None and c.lng is not None:
            item["distance_km"] = round(_haversine_km(lat, lng, c.lat, c.lng), 2)
        else:
            item["distance_km"] = None

        results.append(item)

    if lat is not None and lng is not None:
        results.sort(key=lambda x: (x["distance_km"] is None, x["distance_km"] or 0.0))

    return results[:limit]
