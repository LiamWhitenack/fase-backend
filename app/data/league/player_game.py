from sqlalchemy import (
    Boolean,
    Date,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base


class PlayerGame(Base):
    __tablename__ = "player_games"

    # ---- identifiers ----
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    game_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("games.id"),
        index=True,
        nullable=False,
    )

    player_season_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("player_seasons.id"),
        index=True,
        nullable=False,
    )

    team_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("teams.id"),
        index=True,
        nullable=False,
    )

    opponent_team_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("teams.id"),
        index=True,
        nullable=False,
    )

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

    # ---- advanced ----
    double_double: Mapped[bool] = mapped_column(Boolean)
    triple_double: Mapped[bool] = mapped_column(Boolean)
    usage_rate: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ---- lineup ----
    starting_position: Mapped[str | None] = mapped_column(String, nullable=True)
    started: Mapped[bool] = mapped_column(Boolean)

    # ---- relationships ----
    game = relationship("Game", back_populates="player_games")
    player_season = relationship("PlayerSeason", back_populates="games")

    __table_args__ = (
        Index(
            "ix_player_game_unique",
            "game_id",
            "player_season_id",
            unique=True,
        ),
    )
