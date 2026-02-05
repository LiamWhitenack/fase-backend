from __future__ import annotations

from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    from app.data.league.season import Season


class PlayerGame(Base):
    __tablename__ = "player_games"

    # ---- identifiers ----
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("games.id"), index=True, nullable=False
    )
    player_season_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("player_seasons.id"), index=True, nullable=False
    )
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id"), index=True, nullable=False
    )
    season_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("seasons.id", ondelete="CASCADE"),  # foreign key
        index=True,
        nullable=False,  # or True if some games might not have a season
    )

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

    # ---- lineup ----
    starting_position: Mapped[str | None] = mapped_column(String, nullable=True)
    started: Mapped[bool] = mapped_column(Boolean)

    # ---- advanced stats (cannot be derived from traditional box score) ----
    offensive_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    defensive_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    net_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    assist_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    assist_to_turnover: Mapped[float | None] = mapped_column(Float, nullable=True)
    assist_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    offensive_rebound_percentage: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    defensive_rebound_percentage: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    total_rebound_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    effective_field_goal_percentage: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    true_shooting_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    usage_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    pace: Mapped[float | None] = mapped_column(Float, nullable=True)
    pie: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ---- relationships ----
    season: Mapped[Season] = relationship("Season")
    game = relationship("Game", back_populates="player_games")
    # foreign key linking to PlayerSeason
    player_season_id: Mapped[int] = mapped_column(
        ForeignKey("player_seasons.id"), index=True
    )

    # relationship back to PlayerSeason
    __table_args__ = (
        Index(
            "ix_player_game_unique",
            "game_id",
            "player_season_id",
            unique=True,
        ),
    )

    # ---- helper constructor from advanced boxscore row ----
    @classmethod
    def from_advanced_boxscore(
        cls,
        row: dict,
        game_id: int,
        player_season_id: int,
        team_id: int,
        season: str,
        game_date: str,
        is_home_game: bool,
    ):
        """
        Build a PlayerGame object from a boxscoreadvancedv2 API row.
        """
        # Convert minutes "MM:SS" -> float
        min_str = row.get("MIN", "0:00")
        minutes = 0.0
        if min_str and ":" in min_str:
            mins, secs = map(int, min_str.split(":"))
            minutes = mins + secs / 60

        return cls(
            game_id=game_id,
            player_season_id=player_season_id,
            team_id=team_id,
            season=season,
            game_date=game_date,
            is_home_game=is_home_game,
            minutes_played=minutes,
            points=row.get("PTS"),
            field_goals_made=row.get("FGM"),
            field_goals_attempted=row.get("FGA"),
            three_pointers_made=row.get("FG3M"),
            three_pointers_attempted=row.get("FG3A"),
            free_throws_made=row.get("FTM"),
            free_throws_attempted=row.get("FTA"),
            offensive_rebounds=row.get("OREB"),
            defensive_rebounds=row.get("DREB"),
            total_rebounds=row.get("REB"),
            assists=row.get("AST"),
            steals=row.get("STL"),
            blocks=row.get("BLK"),
            turnovers=row.get("TOV"),
            personal_fouls=row.get("PF"),
            plus_minus=row.get("PLUS_MINUS"),
            started=row.get("START_POSITION") is not None,
            starting_position=row.get("START_POSITION"),
            offensive_rating=row.get("OFF_RATING"),
            defensive_rating=row.get("DEF_RATING"),
            net_rating=row.get("NET_RATING"),
            assist_ratio=row.get("AST_RATIO"),
            assist_to_turnover=row.get("AST_TOV"),
            assist_percentage=row.get("AST_PCT"),
            offensive_rebound_percentage=row.get("OREB_PCT"),
            defensive_rebound_percentage=row.get("DREB_PCT"),
            total_rebound_percentage=row.get("REB_PCT"),
            effective_field_goal_percentage=row.get("EFG_PCT"),
            true_shooting_percentage=row.get("TS_PCT"),
            usage_percentage=row.get("USG_PCT"),
            pace=row.get("PACE"),
            pie=row.get("PIE"),
        )
