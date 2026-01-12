from sqlalchemy import String, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column

from ...base import Base  # wherever your Base lives


class Team(Base):
    __tablename__ = "teams"

    # ---- identifiers ----
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # ---- identity ----
    city: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)
    nickname: Mapped[str] = mapped_column(String, index=True)
    abbreviation: Mapped[str] = mapped_column(String, unique=True, index=True)

    # ---- organization ----
    conference: Mapped[str] = mapped_column(String, index=True)
    division: Mapped[str] = mapped_column(String, index=True)

    __table_args__ = (
        # Prevent duplicate teams like "Los Angeles Lakers"
        Index(
            "ix_team_city_nickname_unique",
            "city",
            "nickname",
            unique=True,
        ),
    )
