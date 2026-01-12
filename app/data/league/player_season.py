from app.base import Base
from app.data.league.player import Player
from app.data.league.team import Team


from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PlayerSeason(Base):
    __tablename__ = "player_seasons"

    # ---- identifiers ----
    id: Mapped[int] = mapped_column(primary_key=True)

    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id"), index=True
    )
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id"), index=True
    )

    season: Mapped[int] = mapped_column(
        Integer, index=True
    )  # e.g. 2023 for 2023–24

    # ---- roster info ----
    jersey_number: Mapped[int | None] = mapped_column(Integer)
    position: Mapped[str | None] = mapped_column()
    is_two_way: Mapped[bool] = mapped_column(Boolean, default=False)

    # ---- season totals ----
    games_played: Mapped[int] = mapped_column(Integer, default=0)
    minutes: Mapped[float] = mapped_column(Float, default=0.0)
    points: Mapped[int] = mapped_column(Integer, default=0)
    assists: Mapped[int] = mapped_column(Integer, default=0)
    rebounds: Mapped[int] = mapped_column(Integer, default=0)
    steals: Mapped[int] = mapped_column(Integer, default=0)
    blocks: Mapped[int] = mapped_column(Integer, default=0)
    turnovers: Mapped[int] = mapped_column(Integer, default=0)
    personal_fouls: Mapped[int] = mapped_column(Integer, default=0)

    # ---- shooting ----
    field_goals_made: Mapped[int] = mapped_column(Integer, default=0)
    field_goals_attempted: Mapped[int] = mapped_column(Integer, default=0)
    three_pointers_made: Mapped[int] = mapped_column(Integer, default=0)
    three_pointers_attempted: Mapped[int] = mapped_column(Integer, default=0)
    free_throws_made: Mapped[int] = mapped_column(Integer, default=0)
    free_throws_attempted: Mapped[int] = mapped_column(Integer, default=0)

    # ---- advanced season metrics ----
    player_efficiency_rating: Mapped[float] = mapped_column(Float, default=0.0)
    true_shooting_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    usage_rate: Mapped[float] = mapped_column(Float, default=0.0)
    offensive_rating: Mapped[float] = mapped_column(Float, default=0.0)
    defensive_rating: Mapped[float] = mapped_column(Float, default=0.0)
    win_shares: Mapped[float] = mapped_column(Float, default=0.0)

    # ---- awards (season-scoped) ----
    is_mvp: Mapped[bool] = mapped_column(Boolean, default=False)
    is_all_nba: Mapped[bool] = mapped_column(Boolean, default=False)
    is_all_defensive: Mapped[bool] = mapped_column(Boolean, default=False)
    is_all_rookie: Mapped[bool] = mapped_column(Boolean, default=False)

    # ---- relationships ----
    player: Mapped[Player] = relationship("Player", back_populates="seasons")
    team: Mapped[Team] = relationship("Team", back_populates="player_seasons")

    __table_args__ = (
        # Enforce exactly one row per player/team/season
        Index(
            "ix_player_season_unique",
            "player_id",
            "team_id",
            "season",
            unique=True,
        ),
    )