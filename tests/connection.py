from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.base import Base
from app.data.league import *

DATABASE_URL = "postgresql+psycopg://athlete_user:athlete_password@localhost:6544/athlete_market_test"

engine = create_engine(
    DATABASE_URL, echo=True
)  # echo=True prints SQL queries for debugging

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


@contextmanager
def get_test_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
