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
    contract: Contract
    season: PlayerSeason | None
    previous_season: PlayerSeason | None
    bio: PlayerBio
    averages: CareerAverages
