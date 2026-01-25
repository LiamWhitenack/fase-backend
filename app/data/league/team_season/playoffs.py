from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base
from app.data.league.team import Team
from app.data.league.team_season.core import TeamSeason


class TeamSeasonPlayoffs(Base):
    __tablename__ = "team_season_playoffs"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_season_id: Mapped[int] = mapped_column(
        ForeignKey("team_seasons.id"),
        unique=True,
    )

    made_playoffs: Mapped[bool] = mapped_column(Boolean)

    rounds_won: Mapped[int] = mapped_column(Integer)
    playoff_wins: Mapped[int] = mapped_column(Integer)
    playoff_losses: Mapped[int] = mapped_column(Integer)

    eliminated_by: Mapped[str | None] = mapped_column(String(64))

    team_season: Mapped[TeamSeason] = relationship(back_populates="playoffs")
