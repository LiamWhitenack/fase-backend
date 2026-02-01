from collections.abc import Iterable

from sqlalchemy.orm import Session

from app.base import Base
from tests.connection import get_test_session


def seed_test_data(session: Session, data: Iterable[Base], /) -> None:
    for datum in data:
        session.add(datum)
        session.commit()
