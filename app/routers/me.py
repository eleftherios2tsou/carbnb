from fastapi import APIRouter, Depends
from app.deps import get_current_user
from app.schemas import UserOut

router = APIRouter(prefix="/me", tags=["me"])

@router.get("", response_model=UserOut)
def me(user = Depends(get_current_user)):
    return user
