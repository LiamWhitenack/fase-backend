from __future__ import annotations

from typing import TYPE_CHECKING

from pandas import Series
from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey, UniqueConstraint

from app.base import Base
from app.data.league.team import Team

if TYPE_CHECKING:
    from app.data.league.season import Season

if TYPE_CHECKING:
    from app.data.league.team_season.draft_picks import DraftPick
    from app.data.league.team_season.finances import TeamSeasonFinance
    from app.data.league.team_season.playoffs import TeamSeasonPlayoffRound


class TeamSeason(Base):
    __tablename__ = "team_seasons"
    __table_args__ = (UniqueConstraint("team_id", "season_id", name="uq_team_season"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)

    season_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("seasons.id", ondelete="CASCADE"),  # foreign key
        index=True,
        nullable=False,  # or True if some games might not have a season
    )

    # Core record
    wins: Mapped[int] = mapped_column(Integer)
    losses: Mapped[int] = mapped_column(Integer)
    win_pct: Mapped[float] = mapped_column(Float)

    # Standings context
    league_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    playoff_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    conference_record: Mapped[str | None] = mapped_column(String(7))
    division_record: Mapped[str | None] = mapped_column(String(7))
    home_record: Mapped[str | None] = mapped_column(String(7))
    road_record: Mapped[str | None] = mapped_column(String(7))
    last_10_record: Mapped[str | None] = mapped_column(String(7))

    conference_games_back: Mapped[float | None] = mapped_column(Float, nullable=True)
    division_games_back: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Scoring
    points_per_game: Mapped[float | None] = mapped_column(Float)
    opp_points_per_game: Mapped[float | None] = mapped_column(Float)
    point_diff_per_game: Mapped[float | None] = mapped_column(Float)

    # Clinch flags
    clinched_conference_title: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )
    clinched_division_title: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    clinched_playoff_birth: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    season: Mapped[Season] = relationship("Season")

    team: Mapped[Team] = relationship(back_populates="seasons")

    finance: Mapped[TeamSeasonFinance] = relationship(
        back_populates="team_season",
        uselist=False,
        cascade="all, delete-orphan",
    )

    playoff_rounds: Mapped[list[TeamSeasonPlayoffRound]] = relationship(
        back_populates="team_season",
        cascade="all, delete-orphan",
        order_by="TeamSeasonPlayoffRound.round",
    )

    draft_picks: Mapped[DraftPick] = relationship(
        back_populates="team_season",
        cascade="all, delete-orphan",
    )

    @classmethod
    def from_league_standings_row(
        cls,
        team_id: int,
        season: int,
        row: Series,
    ) -> TeamSeason:
        return cls(
            team_id=team_id,
            season=season,
            wins=row["WINS"],
            losses=row["LOSSES"],
            win_pct=row["WinPCT"],
            league_rank=int(row["LeagueRank"])
            if row["LeagueRank"] and (row["LeagueRank"] == row["LeagueRank"])
            else None,
            playoff_rank=row["PlayoffRank"],
            conference_record=row["ConferenceRecord"],
            division_record=row["DivisionRecord"],
            home_record=row["HOME"],
            road_record=row["ROAD"],
            last_10_record=row["L10"],
            conference_games_back=row["ConferenceGamesBack"],
            division_games_back=row["DivisionGamesBack"],
            points_per_game=row["PointsPG"],
            opp_points_per_game=row["OppPointsPG"],
            point_diff_per_game=row["DiffPointsPG"],
            clinched_conference_title=row["ClinchedConferenceTitle"],
            clinched_division_title=row["ClinchedDivisionTitle"],
            clinched_playoff_birth=row["ClinchedPlayoffBirth"],
        )
