from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.deps import get_current_user
from app.profiles.models import Profile
from app.profiles.schemas import ProfileOut, ProfileUpsertIn

router = APIRouter(tags=["profiles"])

@router.get("/me/profile", response_model=ProfileOut)
def get_my_profile(db: Session = Depends(get_db), user=Depends(get_current_user)):
    prof = db.get(Profile, user.id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profile not found")
    return prof

@router.put("/me/profile", response_model=ProfileOut)
def upsert_my_profile(body: ProfileUpsertIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    prof = db.get(Profile, user.id)
    if not prof:
        prof = Profile(user_id=user.id, **body.model_dump())
        db.add(prof)
    else:
        for k, v in body.model_dump().items():
            setattr(prof, k, v)
    db.commit()
    db.refresh(prof)
    return prof
