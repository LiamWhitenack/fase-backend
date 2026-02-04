from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime, time
from enum import Enum
from typing import Any

from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeMeta, Session

from app.base import Base
from app.data.connection import Season, get_session
from app.data.league.player import Player


def sqlalchemy_to_dicts(objects: Iterable[Base]) -> list[dict[str, Any]]:
    """
    Convert an iterable of SQLAlchemy model instances into a list of dictionaries
    that can be safely used as seed data across multiple sessions.
    """

    def serialize_value(value: object) -> object:
        """
        Convert non-JSON-safe Python values into a stable Python representation
        (still valid as a Python literal).
        """
        if isinstance(value, Enum):
            return value.value

        if isinstance(value, datetime):
            return {
                "__type__": "datetime",
                "year": value.year,
                "month": value.month,
                "day": value.day,
                "hour": value.hour,
                "minute": value.minute,
                "second": value.second,
                "microsecond": value.microsecond,
            }

        if isinstance(value, date):
            return {
                "__type__": "date",
                "year": value.year,
                "month": value.month,
                "day": value.day,
            }

        if isinstance(value, time):
            return {
                "__type__": "time",
                "hour": value.hour,
                "minute": value.minute,
                "second": value.second,
                "microsecond": value.microsecond,
            }

        return value

    rows: list[dict[str, Any]] = []

    for obj in objects:
        mapper = inspect(obj)

        values: dict[str, Any] = {}
        for column in mapper.mapper.columns:
            attr = column.key
            values[attr] = serialize_value(getattr(obj, attr))

        rows.append(
            {
                "model": obj.__class__.__name__,
                "values": values,
            }
        )

    return rows


def export_rows_as_dict_seed_data(
    session: Session,
    model: type[DeclarativeMeta],
    filter_kwargs: dict | None = None,
    limit: int | None = None,
) -> str:
    """
    Export rows from a SQLAlchemy ORM model as dictionary seed data.
    """
    query = session.query(model)

    if filter_kwargs:
        query = query.filter_by(**filter_kwargs)

    if limit:
        query = query.limit(limit)

    rows = query.all()

    seed_data = sqlalchemy_to_dicts(rows)  # ty:ignore[invalid-argument-type]

    code = "seed_data = " + repr(seed_data)
    return code


def get_player_dicts(
    session: Session,
    player_ids: list[int],
    *,
    include_teams: bool = True,
    include_contracts: bool = True,
    include_salaries: bool = True,
    include_seasons: bool = True,
) -> list[dict[str, Any]]:
    teams: set[int] = set()
    res: list[dict[str, Any]] = []

    for player_id in player_ids:
        player = session.query(Player).where(Player.id == player_id).one()

        if include_teams:
            for season in player.seasons:
                if season.team.id not in teams:
                    res.extend(sqlalchemy_to_dicts([season.team]))
                    teams.add(season.team.id)

            for contract in player.contracts:
                if contract.team.id not in teams:
                    res.extend(sqlalchemy_to_dicts([contract.team]))
                    teams.add(contract.team.id)

        res.extend(sqlalchemy_to_dicts([player]))

        if include_contracts:
            res.extend(sqlalchemy_to_dicts(player.contracts))

        if include_salaries:
            res.extend(sqlalchemy_to_dicts(player.salaries))

        if include_seasons:
            res.extend(sqlalchemy_to_dicts(player.seasons))

    return res


def save_as_python(
    player_ids: list[int],
    path: str = "test.py",
    variable_name: str | None = None,
) -> None:
    with get_session() as session:
        seed_data = get_player_dicts(session, player_ids)

    with open(path, "w") as f:
        f.write("from __future__ import annotations\n\n")
        if variable_name is None:
            variable_name = "seed_data"
        f.write(f"{variable_name} = {repr(seed_data)}\n")


def save_seasons() -> None:
    with get_session() as session:
        code = export_rows_as_dict_seed_data(session, Season)  # ty:ignore[invalid-argument-type]

    with open("tests/data/seasons.py", "w") as f:
        f.write("from __future__ import annotations\n\n")
        f.write(code)
        f.write("\n")


if __name__ == "__main__":
    save_as_python(
        [1630172, 101150, 42, 1630533],
        path="tests/data/williams_contract_data.py",
        variable_name="WILLIAMS_CONTRACT_DATA",
    )
