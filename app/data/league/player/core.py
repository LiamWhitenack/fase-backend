from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import TYPE_CHECKING, Any, Sequence, TypeVar

from sqlalchemy import Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base
from app.custom_types import MLSafe
from app.data.league.player.career_averages import CareerAverages
from app.data.league.player.player_bio import PlayerBio
from app.data.league.player.supporting_contract_info import (
    ContractSupportingInformation,
)
from app.utils.voided_contracts import VOIDED_CONTRACTS_MANAGER

T = TypeVar("T")

if TYPE_CHECKING:
    from app.data.league import Contract
    from app.data.league.player import PlayerSeason
    from app.data.league.team.payroll import TeamPlayerBuyout, TeamPlayerSalary


class Player(Base):
    __tablename__ = "players"
    __allow_unmapped__ = True

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
        "TeamPlayerBuyout",
        back_populates="player",
        cascade="all, delete-orphan",
        overlaps="salaries",
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

    _stats_dict: dict[int, PlayerSeason] | None = None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    @property
    def stats_dict(self) -> dict[int, PlayerSeason]:
        self._stats_dict = getattr(self, "_stats_dict", None)
        if self._stats_dict is None:
            self._stats_dict = {s.season_id: s for s in self.seasons}
            self._stats_dict = self._stats_dict
        return self._stats_dict

    def rebuild_stats_dict(self) -> None:
        self._stats_dict = {s.season_id: s for s in self.seasons}

    def __getitem__(self, season_id: int) -> PlayerSeason:
        return self.stats_dict[season_id]

    def get(self, key: int, default: T | None = None) -> PlayerSeason | T | None:
        return self.stats_dict.get(key, default)

    def __repr__(self) -> str:
        return (
            f"Player("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"first_name={self.first_name!r}, "
            f"last_name={self.last_name!r}, "
            f"position={self.position!r}, "
            f"draft_year={self.draft_year!r}"
            f")"
        )

    @property
    def birth_datetime(self) -> datetime | None:
        if self.birth_date is None:
            return None
        return datetime.fromisoformat(self.birth_date)

    @property
    def career_relative_dollars(self) -> float:
        return sum(s.relative_dollars for s in self.salaries) + sum(
            s.relative_dollars for s in self.buyouts
        )

    @property
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
            career.three_point_made += s.three_pointers_made or 0
            career.three_point_attempted += s.three_pointers_attempted or 0

            career.free_throw_made += s.free_throws_made or 0
            career.free_throw_attempted += s.free_throws_attempted or 0

        if career.games_played > 0:
            # convert totals to per-game
            career.points_pg /= career.games_played
            career.rebounds_pg /= career.games_played
            career.assists_pg /= career.games_played
            career.steals_pg /= career.games_played
            career.blocks_pg /= career.games_played
            career.turnovers_pg /= career.games_played
            career.minutes_per_game /= career.games_played

            def compute_pct(made: float, attempted: float) -> float:
                return made / attempted if attempted > 0 else 0

            career.three_point_pct = compute_pct(
                career.three_point_made, career.three_point_attempted
            )

            career.free_throw_pct = compute_pct(
                career.free_throw_made, career.free_throw_attempted
            )

        return career

    @property
    def bio_complete(self) -> bool:
        return None not in {
            self.height_inches,
            self.weight_pounds,
            self.country,
            self.position,
            self.draft_year,
        }

    @property
    def bio(self) -> PlayerBio:
        data = {
            "height_inches": self.height_inches,
            "weight_pounds": self.weight_pounds,
            "country": self.country,
            "position": self.position,
            "draft_year": self.draft_year,
            "draft_round": self.draft_round,
            "draft_number": self.draft_number,
        }
        for key, value in data.items():
            if value is None and key not in ["draft_round", "draft_number"]:
                raise Exception(f"Missing {key} for bio")

        return PlayerBio(**data)  # ty:ignore[invalid-argument-type]

    def supporting_contract_info(self) -> Iterable[ContractSupportingInformation]:
        salaries = {s.season_id: s for s in self.salaries}
        salary_dollars = {s.season_id: s.dollars for s in self.salaries}
        buyouts = {b.season_id: b for b in self.buyouts}
        dollars = salaries | {
            b.season_id: salary_dollars.get(b.season_id, 0) + b.dollars
            for b in self.buyouts
        }
        contracts = sorted(
            self.contracts, key=lambda c: (c.start_year, (c.value if c.value else 0))
        )
        last_contract_end = -1
        for i, contract in enumerate(contracts, start=1):
            if (
                contract.start_year < last_contract_end
                and contract.start_year not in buyouts
                and (contract.start_year - 1) not in buyouts
            ):
                continue
            if contract.start_year == 2011:
                continue  # we don't actually have all the data we would need for this year
            if contract.start_year not in dollars and (
                contract.duration < 2 or len(dollars) < 3
            ):
                continue  # a short contract I don't have all the data for, I think we'll be okay without it
            if not contract.player.bio_complete:
                continue
            if contract.value is None:
                continue
            if contract.start_year not in dollars:
                if VOIDED_CONTRACTS_MANAGER.voided(contract):
                    continue
                if self.ask_voided(contract):
                    VOIDED_CONTRACTS_MANAGER.add(contract)
                    continue

            salary: TeamPlayerSalary | TeamPlayerBuyout
            if contract.start_year not in salaries:
                if VOIDED_CONTRACTS_MANAGER.voided(contract):
                    continue
                if contract.start_year not in buyouts:
                    VOIDED_CONTRACTS_MANAGER.add(contract)
                    continue
                salary = buyouts[contract.start_year]
            else:
                salary = salaries.pop(contract.start_year)

            yield ContractSupportingInformation(
                self,
                salary,
                contract,
                self.get(contract.start_year - 1),
                self.get(contract.start_year - 2),
                self.career_averages,
                i,
            )
            last_contract_end = contract.start_year + contract.duration

    def ask_voided(self, contract: Contract) -> bool:
        keep = input(
            f"Was {self.name}'s contract from {contract.start_year} voided? (y/n)"
        )

        return keep == "y"
