from __future__ import annotations

import enum
from collections import defaultdict
from typing import TYPE_CHECKING

from nba_api.stats.endpoints import teamgamelog
from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.base import Base

if TYPE_CHECKING:
    from app.data.league import Team, TeamSeason


class PlayoffRound(enum.Enum):
    FIRST_ROUND = "First Round"
    CONF_SEMIS = "Conference Semifinals"
    CONF_FINALS = "Conference Finals"
    FINALS = "NBA Finals"

    @property
    def order(self) -> int:
        return {
            PlayoffRound.FIRST_ROUND: 1,
            PlayoffRound.CONF_SEMIS: 2,
            PlayoffRound.CONF_FINALS: 3,
            PlayoffRound.FINALS: 4,
        }[self]


class TeamSeasonPlayoffRound(Base):
    """WARNING: NOT FINISHED"""

    __tablename__ = "team_season_playoff_rounds"
    __table_args__ = (
        UniqueConstraint(
            "team_season_id",
            "round",
            name="uq_team_season_playoff_round",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    team_season_id: Mapped[int] = mapped_column(
        ForeignKey("team_seasons.id"),
        index=True,
    )

    round: Mapped[PlayoffRound] = mapped_column(
        Enum(PlayoffRound, name="playoff_round"),
    )

    wins: Mapped[int] = mapped_column(Integer)
    losses: Mapped[int] = mapped_column(Integer)

    won_round: Mapped[bool] = mapped_column(Boolean)

    eliminated_by_team_id: Mapped[int | None] = mapped_column(
        ForeignKey("teams.id"),
        nullable=True,
    )

    team_season: Mapped[TeamSeason] = relationship(back_populates="playoff_rounds")

    @classmethod
    def from_nba_api(
        cls,
        *,
        session: Session,
        team_season: TeamSeason,
        nba_team_id: int,
    ) -> list["TeamSeasonPlayoffRound"]:
        games = teamgamelog.TeamGameLog(
            team_id=nba_team_id,
            season=team_season.season_id,
            season_type_all_star="Playoffs",
        ).get_data_frames()[0]

        if games.empty:
            return []

        series_map = defaultdict(list)

        for _, row in games.iterrows():
            opponent = row["MATCHUP"].split(" ")[-1]
            series_map[opponent].append(row)

        playoff_rounds = []

        for index, (opponent_abbr, games) in enumerate(series_map.items(), start=1):
            round_enum = PlayoffRound()

            wins = sum(1 for g in games if g["WL"] == "W")
            losses = sum(1 for g in games if g["WL"] == "L")
            won_round = wins > losses

            eliminated_by_team_id = None
            if not won_round:
                eliminated_by_team_id = (
                    session.query(Team.id)
                    .filter(Team.abbreviation == opponent_abbr)
                    .scalar()
                )

            playoff_rounds.append(
                cls(
                    team_season_id=team_season.id,
                    round=round_enum,
                    wins=wins,
                    losses=losses,
                    won_round=won_round,
                    eliminated_by_team_id=eliminated_by_team_id,
                )
            )

        return playoff_rounds
