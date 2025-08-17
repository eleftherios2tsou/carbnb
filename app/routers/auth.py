from fastapi import APIRouter, Depends, HTTPException, status
from app import models, schemas, utils
from app.db import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session=Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = utils.hash_password(user_in.password)
    user = models.User(email=user_in.email, hashed_password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login")
def login(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if not user or not utils.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    from app.jwt import create_access_token
    return {"access_token": create_access_token(str(user.id)), "token_type": "bearer"}

