from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from sqlalchemy import Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base
from app.custom_types import MLSafe

if TYPE_CHECKING:
    from app.data.league import Contract
    from app.data.league.player import PlayerSeason
    from app.data.league.team.payroll import TeamPlayerBuyout, TeamPlayerSalary


@dataclass
class CareerAverages:
    games_played: int = 0

    points_pg: float = 0
    rebounds_pg: float = 0
    assists_pg: float = 0
    steals_pg: float = 0
    blocks_pg: float = 0
    turnovers_pg: float = 0
    minutes_per_game: float = 0

    field_goal_pct: float = 0
    three_point_pct: float = 0
    free_throw_pct: float = 0


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
    seasons: Mapped[list[PlayerSeason]] = relationship(
        "PlayerSeason",
        back_populates="player",
        cascade="all, delete-orphan",
    )

    salaries: Mapped[list[TeamPlayerSalary]] = relationship(
        "TeamPlayerSalary",
        back_populates="player",
        cascade="all, delete-orphan",
    )

    buyouts: Mapped[list[TeamPlayerBuyout]] = relationship(
        "TeamPlayerSalary",
        back_populates="player",
        cascade="all, delete-orphan",
    )

    contracts: Mapped[list[Contract]] = relationship(
        "Contract",
        back_populates="player",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_player_name", "name"),
        Index("ix_player_last_first", "last_name", "first_name"),
        Index("ix_player_draft", "draft_year", "draft_round", "draft_number"),
    )

    def __post_init__(self) -> None:
        self.stats_dict = {s.season_id: s for s in self.seasons}
        # self.salaries_dict = {s.season_id: s for s in self.salaries}
        # self.buyouts_dict = {s.season_id: s for s in self.buyouts}

    def __getitem__(self, season_id: int) -> PlayerSeason:
        return self.stats_dict[season_id]

    @property
    def career_relative_dollars(self) -> float:
        return sum(s.relative_dollars for s in self.salaries) + sum(
            s.relative_dollars for s in self.buyouts
        )

    def career_averages(self) -> CareerAverages:
        career = CareerAverages()

        for s in self.seasons:
            if not s.games_played or s.games_played <= 0:
                continue

            career.games_played += s.games_played

            # increment totals
            career.points_pg += s.points or 0
            career.rebounds_pg += s.rebounds or 0
            career.assists_pg += s.assists or 0
            career.steals_pg += s.steals or 0
            career.blocks_pg += s.blocks or 0
            career.turnovers_pg += s.turnovers or 0
            career.minutes_per_game += s.minutes_per_game or 0

            # accumulate makes/attempts for percentages
            career.field_goal_pct += s.field_goals_made or 0
            career.field_goal_pct += -(
                s.field_goals_attempted or 0
            )  # temporarily store attempts as negative
            career.three_point_pct += s.three_pointers_made or 0
            career.three_point_pct += -(s.three_pointers_attempted or 0)
            career.free_throw_pct += s.free_throws_made or 0
            career.free_throw_pct += -(s.free_throws_attempted or 0)

        if career.games_played > 0:
            # convert totals to per-game
            career.points_pg /= career.games_played
            career.rebounds_pg /= career.games_played
            career.assists_pg /= career.games_played
            career.steals_pg /= career.games_played
            career.blocks_pg /= career.games_played
            career.turnovers_pg /= career.games_played
            career.minutes_per_game /= career.games_played

            # convert shooting totals to percentages
            def compute_pct(m_a: float) -> float:
                made, attempted = m_a, -m_a
                return made / attempted if attempted > 0 else 0

            career.field_goal_pct = compute_pct(career.field_goal_pct)
            career.three_point_pct = compute_pct(career.three_point_pct)
            career.free_throw_pct = compute_pct(career.free_throw_pct)

        return career
