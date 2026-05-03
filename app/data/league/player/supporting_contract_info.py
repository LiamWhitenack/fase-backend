from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Literal

from app.custom_types import MLSafe

if TYPE_CHECKING:
    from app.data.league import (
        Contract,
        Player,
        PlayerSeason,
        TeamPlayerBuyout,
        TeamPlayerSalary,
    )
    from app.data.league.player.career_averages import CareerAverages
    from app.data.league.player.player_bio import PlayerBio


@dataclass()
class ContractSupportingInformation:
    player: Player
    season_id: int
    contract_number: int
    averages: CareerAverages
    salary: TeamPlayerSalary | TeamPlayerBuyout | None
    contract: Contract | None
    contract_season: PlayerSeason | None
    previous_season: PlayerSeason | None

    def __post_init__(self) -> None:
        super().__init__()
        if self.season_id is None:
            raise
        if self.contract is None:
            if self.salary is None and not self.is_buyout():
                raise Exception()

    def to_scalar(self) -> dict[str, MLSafe | None]:
        return (
            {
                "buyout": not hasattr(self.salary, "apron_salary"),
                "season": self.season_id,
                "contract_number": self.contract_number,
                "ascending": None
                if self.contract is None or self.is_buyout()
                else self.is_ascending(),
            }
            | (
                blank_contract_scalar()
                if self.contract is None
                else self.contract.to_scalar()
            )
            | (
                self.salary.to_scalar()
                if self.salary is not None
                else blank_salary_scalar()
            )
            | {
                "contract_season_" + k: v
                for k, v in (
                    self.contract_season.ml_data().no_colinearity()
                    if self.contract_season is not None
                    else blank_season_ml_data()
                ).items()
            }
            | {
                "previous_season_" + k: v
                for k, v in (
                    self.previous_season.ml_data().no_colinearity()
                    if self.previous_season is not None
                    else blank_season_ml_data()
                ).items()
            }
            | self.player.bio.to_scalar()
            | {"age": self.age()}
            | self.averages.to_scalar()
        )

    def is_buyout(self) -> bool:
        return not hasattr(self.salary, "luxury_tax")

    def is_ascending(self) -> Literal[1, 0, -1, None]:
        if (
            self.contract is None
            or self.contract.value is None
            or self.contract.duration is None
            or self.salary is None
            or self.salary.dollars is None
        ):
            return None
        avg = self.contract.value / self.contract.duration
        avg_div_first = self.salary.dollars / avg * 100 // 4 / 25
        ascending: Literal[-1, 0, 1] = (
            1 if avg_div_first < 1 else (0 if avg_div_first == 1 else -1)
        )

        return ascending

    def age(self) -> int:
        if self.player.birth_datetime is None:
            raise Exception()
        return (datetime(self.season_id + 1, 1, 1) - self.player.birth_datetime).days


def blank_contract_scalar() -> dict[str, None]:
    return {
        "team": None,
        "duration": None,
        # "player_option": self.option_2 == "Player",
        # "team_options": [self.option_1, self.option_2].count("Team"),
    }


def blank_salary_scalar() -> dict[str, None]:
    return {
        "dollars": 0.0,
        "relative_dollars": 0.0,
        "team_id": None,
        "cap_hit_percent": None,
        "salary": None,
        "apron_salary": None,
        "luxury_tax": None,
        "cash_total": None,
        "cash_garunteed": None,
    }


def blank_buyout_scalar() -> dict[str, None]:
    return {
        key: None
        for key in [
            "buyout_dollars",
            "buyout_relative_dollars",
            "buyout_team_id",
            "buyout_player_id",
            "buyout_salary",
        ]
    }


def blank_season_ml_data() -> dict[str, None]:
    return {
        key: None
        for key in [
            "games_played",
            "minutes_per_game",
            "points_pg",
            "rebounds_pg",
            "assists_pg",
            "steals_pg",
            "blocks_pg",
            "turnovers_pg",
            "personal_fouls_pg",
            "field_goals_made_pg",
            "field_goals_attempted_pg",
            "three_pointers_made_pg",
            "three_pointers_attempted_pg",
            "two_pointers_made_pg",
            "two_pointers_attempted_pg",
            "free_throws_made_pg",
            "free_throws_attempted_pg",
            "field_goal_pct",
            "three_point_pct",
            "two_point_pct",
            "free_throw_pct",
            "assist_percentage",
            "assist_to_turnover",
            "assist_ratio",
            "offensive_rebound_pct",
            "defensive_rebound_pct",
            "rebound_pct",
            "turnover_pct",
            "usage_pct",
            "offensive_rating",
            "defensive_rating",
            "net_rating",
            "estimated_offensive_rating",
            "estimated_defensive_rating",
            "estimated_net_rating",
            "estimated_pace",
            "possessions",
            "pts_off_tov",
            "pts_fb",
            "pts_paint",
            "opp_pts_off_tov",
            "opp_pts_fb",
            "opp_pts_paint",
            "plus_minus_pg",
        ]
    }
