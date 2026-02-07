from sqlalchemy import Float, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base
from app.data.league.player.core import Player
from app.data.league.season import Season
from app.data.league.team.core import Team


class PlayerSeason(Base):
    __tablename__ = "player_seasons"

    # ---- identifiers ----
    id: Mapped[int] = mapped_column(primary_key=True)

    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)

    season_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("seasons.id", ondelete="CASCADE"),  # foreign key
        index=True,
        nullable=False,  # or True if some games might not have a season
    )

    # ---- basic context ----
    age: Mapped[float | None] = mapped_column(Float)
    games_played: Mapped[int] = mapped_column(Integer)
    wins: Mapped[int] = mapped_column(Integer)
    losses: Mapped[int] = mapped_column(Integer)
    win_pct: Mapped[float] = mapped_column(Float)
    minutes_per_game: Mapped[float] = mapped_column(Float)

    # ---- ratings ----
    offensive_rating: Mapped[float] = mapped_column(Float)
    defensive_rating: Mapped[float] = mapped_column(Float)
    net_rating: Mapped[float] = mapped_column(Float)

    estimated_offensive_rating: Mapped[float | None] = mapped_column(Float)
    estimated_defensive_rating: Mapped[float | None] = mapped_column(Float)
    estimated_net_rating: Mapped[float | None] = mapped_column(Float)

    # ----  percentages ----
    assist_percentage: Mapped[float] = mapped_column(Float)
    assist_to_turnover: Mapped[float] = mapped_column(Float)
    assist_ratio: Mapped[float] = mapped_column(Float)

    offensive_rebound_pct: Mapped[float] = mapped_column(Float)
    defensive_rebound_pct: Mapped[float] = mapped_column(Float)
    rebound_pct: Mapped[float] = mapped_column(Float)

    turnover_pct: Mapped[float] = mapped_column(Float)
    effective_fg_pct: Mapped[float] = mapped_column(Float)
    true_shooting_pct: Mapped[float] = mapped_column(Float)
    usage_pct: Mapped[float] = mapped_column(Float)

    # ---- pace & impact ----
    pace: Mapped[float] = mapped_column(Float)
    pace_per_40: Mapped[float] = mapped_column(Float)
    estimated_pace: Mapped[float | None] = mapped_column(Float)

    possessions: Mapped[int] = mapped_column(Integer)
    pie: Mapped[float] = mapped_column(Float)

    # ---- shooting volume ----
    field_goals_made: Mapped[int] = mapped_column(Integer)
    field_goals_attempted: Mapped[int] = mapped_column(Integer)
    field_goal_pct: Mapped[float] = mapped_column(Float)

    field_goals_made_pg: Mapped[float] = mapped_column(Float)
    field_goals_attempted_pg: Mapped[float] = mapped_column(Float)

    # ---- relationships ----
    season: Mapped[Season] = relationship("Season")
    player: Mapped[Player] = relationship(back_populates="seasons")
    team: Mapped[Team] = relationship(back_populates="player_seasons")

    __table_args__ = (
        Index(
            "ix_player_season_unique",
            "player_id",
            "team_id",
            "season_id",
            unique=True,
        ),
    )
