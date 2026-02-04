from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.base import Base
from app.data.league import *
from tests.data.seasons import SEASON_DATA

DATABASE_URL = "postgresql+psycopg://athlete_user:athlete_password@localhost:6544/athlete_market_test"

engine = create_engine(
    DATABASE_URL, echo=True
)  # echo=True prints SQL queries for debugging

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def seed_seasons(session: Session) -> None:
    from tests.data.seasons import SEASON_DATA

    session.add_all(SEASON_DATA)
    session.commit()


@contextmanager
def get_test_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    seed_seasons(session)
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()
