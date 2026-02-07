from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base

if TYPE_CHECKING:
    from app.data.league import TeamSeason
    from app.data.league.team.core import Team


class DraftPick(Base):
    __tablename__ = "draft_picks"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_season_id: Mapped[int] = mapped_column(
        ForeignKey("team_seasons.id"),
        index=True,
    )

    year: Mapped[int] = mapped_column(Integer)
    round: Mapped[int] = mapped_column(Integer)

    original_team: Mapped[str] = mapped_column(String(64))
    via_trade: Mapped[bool] = mapped_column(Boolean)

    protected: Mapped[bool] = mapped_column(Boolean)
    protection_notes: Mapped[str | None] = mapped_column(String(255))

    team_season: Mapped[TeamSeason] = relationship(back_populates="draft_picks")
