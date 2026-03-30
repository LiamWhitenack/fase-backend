from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.data.league import Contract, PlayerSeason
    from app.data.league.player.career_averages import CareerAverages
    from app.data.league.player.player_bio import PlayerBio


@dataclass()
class ContractSupportingInformation:
    target: float
    season_id: int
    contract: Contract
    contract_season: PlayerSeason | None
    previous_season: PlayerSeason | None
    bio: PlayerBio
    averages: CareerAverages

    @property
    def is_rookie_contract(self) -> bool:
        return self.contract_season is None and self.bio.draft_year + 3 > self.season_id
