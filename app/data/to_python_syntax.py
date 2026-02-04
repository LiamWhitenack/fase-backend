from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from datetime import date, datetime, time
from enum import Enum
from typing import LiteralString

from sqlalchemy import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeMeta, Session

from app.base import Base
from app.data.connection import Season, get_session
from app.data.league.player import Player


def sqlalchemy_to_syntax(objects: Iterable[Base]) -> list[str]:
    """
    Convert an iterable of SQLAlchemy model instances into Python constructor syntax.
    """

    def serialize_value(value: object) -> str:
        if isinstance(value, Enum):
            return repr(value.value)

        if isinstance(value, datetime):
            return (
                "datetime("
                f"{value.year}, {value.month}, {value.day}, "
                f"{value.hour}, {value.minute}, {value.second}, "
                f"{value.microsecond}"
                ")"
            )

        if isinstance(value, date):
            return f"date({value.year}, {value.month}, {value.day})"

        if isinstance(value, time):
            return (
                "time("
                f"{value.hour}, {value.minute}, {value.second}, "
                f"{value.microsecond}"
                ")"
            )

        if isinstance(value, str):
            return repr(value)

        if value is None:
            return "None"

        return repr(value)

    lines: list[str] = []

    for obj in objects:
        mapper = inspect(obj)
        class_name = obj.__class__.__name__

        kwargs = []
        for column in mapper.mapper.columns:
            attr = column.key
            value = getattr(obj, attr)
            kwargs.append(f"{attr}={serialize_value(value)}")

        line = f"{class_name}({', '.join(kwargs)})"
        lines.append(line)

    return lines


def sqlalchemy_syntax_to_list(syntax_lines: list[str]) -> str:
    """
    Takes a list of SQLAlchemy constructor lines (strings) and returns
    a single string representing a Python list of those objects.
    """
    # Remove any empty lines just in case
    syntax_lines = [line for line in syntax_lines if line.strip()]

    # Join lines with commas and wrap in brackets
    list_syntax = "[\n    " + ",\n    ".join(syntax_lines) + "\n]"
    return list_syntax


def export_rows_as_orm_code(
    session: Session,
    model: type[DeclarativeMeta],
    filter_kwargs: dict | None = None,
    limit: int | None = None,
) -> str:
    """
    Export rows from a SQLAlchemy ORM model as Python code with ORM instances.

    Args:
        session: SQLAlchemy Session connected to source DB.
        model: SQLAlchemy ORM class.
        filter_kwargs: Optional dictionary of filters for the query.
        limit: Optional integer limit on rows to export.

    Returns:
        str: Python code defining a list of ORM instances, ready to paste.
    """
    query = session.query(model)
    if filter_kwargs:
        query = query.filter_by(**filter_kwargs)
    if limit:
        query = query.limit(limit)

    rows = query.all()

    lines = []
    for row in rows:
        fields = ", ".join(
            f"{col.name}={repr(getattr(row, col.name))}"
            for col in row.__table__.columns  # type: ignore[possibly-missing-attribute]
        )
        lines.append(f"{model.__name__}({fields})")

    code = "seed_data = [\n  " + ",\n  ".join(lines) + "\n]"
    return code


def get_player_syntax(
    session: Session,
    player_ids: list[int],
    *,
    include_teams: bool = True,
    include_contracts: bool = True,
    include_salaries: bool = True,
    include_seasons: bool = True,
) -> list[str]:
    teams: set[int] = set()
    res: list[str] = []
    for player_id in player_ids:
        player = session.query(Player).where(Player.id == player_id).one()
        if include_teams:
            for season in player.seasons:
                if season.team.id not in teams:
                    res.extend(sqlalchemy_to_syntax([season.team]))
                    teams.add(season.team.id)
            for contract in player.contracts:
                if contract.team.id not in teams:
                    res.extend(sqlalchemy_to_syntax([contract.team]))
                    teams.add(contract.team.id)
        res.extend(sqlalchemy_to_syntax([player]))
        if include_contracts:
            res.extend(sqlalchemy_to_syntax(player.contracts))
        if include_salaries:
            res.extend(sqlalchemy_to_syntax(player.salaries))
        if include_seasons:
            res.extend(sqlalchemy_to_syntax(player.seasons))

    return res


def save_as_python(
    player_ids: list[int], path: str = "test.py", variable_name: str | None = None
) -> None:
    with get_session() as session:
        with open(path, "w") as f:
            f.write("from app.data.league import *\n\n")
            if variable_name is not None:
                f.write(variable_name + " = ")
            f.write(sqlalchemy_syntax_to_list(get_player_syntax(session, player_ids)))


def save_seasons() -> None:
    with get_session() as session:
        with open("tests/data/seasons.py", "w") as f:
            f.write("from app.data.connection import Season\n\n")
            f.write(export_rows_as_orm_code(session, Season))


if __name__ == "__main__":
    save_as_python(
        [
            1425,
            1626210,
            1631214,
            1541,
            1642873,
            78539,
            78540,
            78564,
            1585,
            1630314,
            433,
            203710,
            78547,
            78541,
            78543,
            1642262,
            101258,
            101114,
            202682,
            78545,
            1631495,
            78546,
            202343,
            677,
            2421,
            78548,
            1629684,
            78549,
            78550,
            1006,
            73,
            1631114,
            1715,
            101214,
            2398,
            1631119,
            420,
            966,
            78554,
            1629140,
            202716,
            200818,
            78555,
            1629026,
            78556,
            31,
            101150,
            1642013,
            200766,
            201173,
            1631109,
            101107,
            52,
            78558,
            78560,
            2590,
            42,
            78561,
            1631466,
            1630172,
            78566,
            78571,
            199,
            202130,
            78563,
            78565,
            78567,
            78568,
            78569,
            281,
            201157,
            1742,
            200761,
            200749,
            78570,
            201944,
            1576,
            1627786,
            1005,
            78573,
            78574,
            1630533,
            1629057,
            1628475,
            1631246,
        ],
        path="tests/data/williams_contract_data.py",
        variable_name="WILLIAMS_CONTRACT_DATA",
    )
