from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.base import Base

DATABASE_URL = (
    "postgresql+psycopg://athlete_user:athlete_password@localhost:6543/athlete_market"
)

engine = create_engine(
    DATABASE_URL, echo=True
)  # echo=True prints SQL queries for debugging

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
session = Session(engine)
