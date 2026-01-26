from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base
from app.data.league.team import Team

if TYPE_CHECKING:
    from app.data.league.team_season.draft_picks import DraftPick
    from app.data.league.team_season.finances import TeamSeasonFinance
    from app.data.league.team_season.playoffs import TeamSeasonPlayoffs


class TeamSeason(Base):
    __tablename__ = "team_seasons"
    __table_args__ = (UniqueConstraint("team_id", "season", name="uq_team_season"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)

    season: Mapped[str] = mapped_column(String(9))  # e.g. "2023-24"

    wins: Mapped[int] = mapped_column(Integer)
    losses: Mapped[int] = mapped_column(Integer)

    team: Mapped[Team] = relationship(back_populates="seasons")

    finance: Mapped[TeamSeasonFinance] = relationship(
        back_populates="team_season",
        uselist=False,
        cascade="all, delete-orphan",
    )

    playoffs: Mapped[TeamSeasonPlayoffs] = relationship(
        back_populates="team_season",
        uselist=False,
        cascade="all, delete-orphan",
    )

    draft_picks: Mapped[DraftPick] = relationship(
        back_populates="team_season",
        cascade="all, delete-orphan",
    )
