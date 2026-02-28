# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tracker.domain.db_models import Base  # adjust import path

DB_URL = "sqlite:///tracker/data/sharelaps.db"

engine = create_engine(DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

def get_session():
    return SessionLocal()

def del_db():
    Base.metadata.drop_all(engine)