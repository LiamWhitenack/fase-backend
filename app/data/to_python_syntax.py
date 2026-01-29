from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session

from app.data.connection import get_session
from app.data.league.player import Player


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


if __name__ == "__main__":
    with get_session() as session:
        with open("test.py", "w") as f:
            f.write(export_rows_as_orm_code(session, Player))  # type: ignore
