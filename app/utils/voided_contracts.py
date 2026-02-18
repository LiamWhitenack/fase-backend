from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.data.league import Contract, Player


class VoidedContractsManager:
    def __init__(self) -> None:
        with open("data/voided-contracts.json") as f:
            self.voided_contracts: list[list[int]] = json.load(f)

    def voided(self, contract: Contract) -> bool:
        return [
            contract.player_id,
            contract.team_id,
            contract.start_year,
        ] in self.voided_contracts

    def add(self, contract: Contract) -> None:
        self.voided_contracts.append(
            [
                contract.player_id,
                contract.team_id,
                contract.start_year,
            ]
        )
        self.save()

    def save(self) -> None:
        with open("data/voided-contracts.json", "w") as f:
            json.dump(sorted(self.voided_contracts), f)


VOIDED_CONTRACTS_MANAGER = VoidedContractsManager()
