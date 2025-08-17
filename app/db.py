from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

engine = create_engine(str(settings.database_url))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit= False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal
    try:
        yield db
    finally:
        db.close()