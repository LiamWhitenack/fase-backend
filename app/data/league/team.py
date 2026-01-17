from sqlalchemy import Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base


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

    # ---- relationships ----
    player_season_teams = relationship(
        lambda: __import__(
            "app.data.league.player", fromlist=["PlayerSeasonTeam"]
        ).PlayerSeasonTeam,
        back_populates="team",
        cascade="all, delete-orphan",
    )
    contracts = relationship(
        "Contract",
        back_populates="team",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        # Prevent duplicate teams like "Los Angeles Lakers"
        Index(
            "ix_team_city_nickname_unique",
            "city",
            "nickname",
            unique=True,
        ),
    )
