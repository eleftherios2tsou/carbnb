from fastapi import APIRouter
from sqlalchemy import text
from app.db import engine

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/db")
def db_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"db_ok": True}
    except Exception as e:
        return {"db_ok": False, "error": str(e)}
