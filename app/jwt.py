from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError

JWT_SECRET = "test"
JWT_ALG = "HS256"
JWT_TTL_MIN = 60 * 24 * 7

def create_access_token(sub: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=JWT_TTL_MIN)
    return jwt.encode({"sub": sub, "exp": exp}, JWT_SECRET, algorithm=JWT_ALG)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])