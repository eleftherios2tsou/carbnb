from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.jwt import decode_access_token
from jose import JWTError

bearer = HTTPBearer(auto_error=False)

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer),
                     db: Session = Depends(get_db)) -> User:
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_access_token(creds.credentials)
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
