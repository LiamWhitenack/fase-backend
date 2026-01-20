from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base import Base
from .team import Team


class Game(Base):
    __tablename__ = "games"

    # ---- identifiers ----
    id: Mapped[int] = mapped_column(primary_key=True)

    # ---- core game info ----
    date: Mapped[date] = mapped_column(Date, index=True)
    season: Mapped[int] = mapped_column(Integer, index=True)

    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)

    # ---- scores ----
    home_team_score: Mapped[int] = mapped_column(Integer)
    away_team_score: Mapped[int] = mapped_column(Integer)
    winning_team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id"), index=True, nullable=True
    )

    # ---- optional metadata ----
    attendance: Mapped[int] = mapped_column(Integer, default=0)
    overtime_periods: Mapped[int] = mapped_column(Integer, default=0)
    neutral_site: Mapped[bool] = mapped_column(Boolean, default=False)
    game_type: Mapped[str] = mapped_column(String, default="Regular")

    winning_team: Mapped[Team] = relationship("Team", foreign_keys=[winning_team_id])
    player_games = relationship(
        "PlayerGame",
        back_populates="game",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        # Prevent duplicate games for same home/away/date
        Index("ix_game_unique", "date", "home_team_id", "away_team_id", unique=True),
        Index("ix_game_home_team", "home_team_id"),
        Index("ix_game_away_team", "away_team_id"),
        Index("ix_game_winning_team", "winning_team_id"),
    )
