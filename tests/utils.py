from collections.abc import Iterable
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy.orm.clsregistry import ClsRegistryToken

from app.base import Base
from app.data.league import *


def get_model_class(model_name: str) -> type[Base]:
    model = Base.registry._class_registry.get(model_name)

    if model is None:
        raise ValueError(f"Model '{model_name}' not found in SQLAlchemy registry")

    return model  # ty:ignore[invalid-return-type]


def delete_all_tables(session: Session) -> None:
    # Get all table names in order of dependencies
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()


def seed_test_data(session: Session, data: Iterable[dict[str, Any]], /) -> None:
    delete_all_tables(session)
    from tests.data.seasons import SEASON_DATA

    data = SEASON_DATA + list(data)
    for row in data:
        model_class = get_model_class(row["model"])
        session.add(model_class(**row["values"]))

    session.commit()
