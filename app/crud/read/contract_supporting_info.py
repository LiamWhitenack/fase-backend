from collections.abc import Iterable

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.data.league import Contract, Player
from app.data.league.player.supporting_contract_info import (
    ContractSupportingInformation,
)


def get_all_contract_supporting_info(
    session: Session,
) -> Iterable[ContractSupportingInformation]:
    stmt = select(Player).where(exists().where(Contract.player_id == Player.id))
    count: int = 0
    for player in session.scalars(stmt).all():
        if not player.draft_year:
            continue
        for i, contract_supporting_info in enumerate(
            sorted(
                list(player.supporting_contract_info()),
                key=lambda csi: csi.contract.start_year,
            )
        ):
            if contract_supporting_info.previous_season is None and i != 0:
                print(
                    f"a missed season for {player.name} in {contract_supporting_info.contract.start_year - 1}!"
                )
                continue
            yield contract_supporting_info
