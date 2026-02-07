from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base

if TYPE_CHECKING:
    from app.data.league import TeamSeason
    from app.data.league.team.core import Team


class TeamSeasonFinance(Base):
    __tablename__ = "team_season_finances"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_season_id: Mapped[int] = mapped_column(
        ForeignKey("team_seasons.id"),
        unique=True,
    )

    total_salary: Mapped[Numeric] = mapped_column(Numeric(14, 2))
    luxury_tax_paid: Mapped[Numeric] = mapped_column(Numeric(14, 2))

    over_first_apron: Mapped[bool] = mapped_column(Boolean)
    over_second_apron: Mapped[bool] = mapped_column(Boolean)

    team_season: Mapped[TeamSeason] = relationship(back_populates="finance")
