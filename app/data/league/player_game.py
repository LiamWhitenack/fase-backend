from sqlalchemy import (
    String,
    Integer,
    Float,
    Boolean,
    Date,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.base import Base


class PlayerGame(Base):
    __tablename__ = "player_games"

    # ---- identifiers ----
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[str] = mapped_column(String, index=True)
    player_id: Mapped[str] = mapped_column(String, index=True)
    team_id: Mapped[str] = mapped_column(String, index=True)
    opponent_team_id: Mapped[str] = mapped_column(String, index=True)

    season: Mapped[str] = mapped_column(String, index=True)
    game_date: Mapped[Date] = mapped_column(Date, index=True)
    is_home_game: Mapped[bool] = mapped_column(Boolean)

    # ---- playing time ----
    minutes_played: Mapped[float] = mapped_column(Float)

    # ---- scoring ----
    points: Mapped[int] = mapped_column(Integer)

    field_goals_made: Mapped[int] = mapped_column(Integer)
    field_goals_attempted: Mapped[int] = mapped_column(Integer)

    three_pointers_made: Mapped[int] = mapped_column(Integer)
    three_pointers_attempted: Mapped[int] = mapped_column(Integer)

    free_throws_made: Mapped[int] = mapped_column(Integer)
    free_throws_attempted: Mapped[int] = mapped_column(Integer)

    # ---- rebounding ----
    offensive_rebounds: Mapped[int] = mapped_column(Integer)
    defensive_rebounds: Mapped[int] = mapped_column(Integer)
    total_rebounds: Mapped[int] = mapped_column(Integer)

    # ---- playmaking ----
    assists: Mapped[int] = mapped_column(Integer)

    # ---- defense ----
    steals: Mapped[int] = mapped_column(Integer)
    blocks: Mapped[int] = mapped_column(Integer)

    # ---- misc ----
    turnovers: Mapped[int] = mapped_column(Integer)
    personal_fouls: Mapped[int] = mapped_column(Integer)
    plus_minus: Mapped[int] = mapped_column(Integer)

    # ---- advanced / box score extras ----
    double_double: Mapped[bool] = mapped_column(Boolean)
    triple_double: Mapped[bool] = mapped_column(Boolean)
    usage_rate: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ---- lineup / role ----
    starting_position: Mapped[str | None] = mapped_column(String, nullable=True)
    started: Mapped[bool] = mapped_column(Boolean)

    # ---- indexes ----
    __table_args__ = (
        Index("ix_player_game_unique", "game_id", "player_id", unique=True),
    )
