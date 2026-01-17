from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base
from app.data.league.team import Team


class Player(Base):
    __tablename__ = "players"

    # ---- identifiers ----
    id: Mapped[int] = mapped_column(primary_key=True)

    # ---- identity ----
    name: Mapped[str] = mapped_column(String, index=True)
    first_name: Mapped[str | None] = mapped_column(String)
    last_name: Mapped[str | None] = mapped_column(String)

    # ---- biographical info (career-level) ----
    height_inches: Mapped[int | None] = mapped_column(Integer)
    weight_pounds: Mapped[int | None] = mapped_column(Integer)
    birth_date: Mapped[str | None] = mapped_column(String)
    country: Mapped[str | None] = mapped_column(String)

    # ---- basketball info (career-level) ----
    school: Mapped[str | None] = mapped_column(String)
    position: Mapped[str | None] = mapped_column(String)

    draft_year: Mapped[int | None] = mapped_column(Integer)
    draft_round: Mapped[int | None] = mapped_column(Integer)
    draft_number: Mapped[int | None] = mapped_column(Integer)

    roster_status: Mapped[int | None] = mapped_column(Integer)  # 1 = active, 0 = not
    is_gleague_player: Mapped[bool | None] = mapped_column(
        Integer
    )  # convert Y/N → True/False

    # ---- relationships ----
    seasons = relationship(
        "PlayerSeasonTeam",
        back_populates="player",
        cascade="all, delete-orphan",
    )
    salaries = relationship(
        "TeamPlayerSalary",
        back_populates="player",
        cascade="all, delete-orphan",
    )
    contracts = relationship(
        "Contract",
        back_populates="player",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_player_name", "name"),
        Index("ix_player_last_first", "last_name", "first_name"),
        Index("ix_player_draft", "draft_year", "draft_round", "draft_number"),
    )


class PlayerSeasonTeam(Base):
    __tablename__ = "player_season_teams"

    # ---- identifiers ----
    id: Mapped[int] = mapped_column(primary_key=True)

    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)

    season: Mapped[int] = mapped_column(Integer, index=True)  # e.g. 2023 for 2023–24

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

    # ---- relationships ----
    player: Mapped["Player"] = relationship("Player", back_populates="seasons")
    team: Mapped["Team"] = relationship("Team", back_populates="player_season_teams")
    games = relationship(
        "PlayerGame",
        back_populates="player_season_team",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        # Enforce exactly one row per player/team/season
        Index(
            "ix_player_season_team_unique",
            "player_id",
            "team_id",
            "season",
            unique=True,
        ),
    )
