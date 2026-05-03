from collections.abc import Iterable

from pandas import DataFrame
from sqlalchemy import and_, create_engine, exists, select
from sqlalchemy.orm import Session, sessionmaker

from app.base import Base
from app.data.connection import get_session
from app.data.league import Contract, Player, PlayerSeason
from app.data.league.player.supporting_contract_info import (
    ContractSupportingInformation,
)


def get_all_contract_supporting_info(
    session: Session,
) -> Iterable[ContractSupportingInformation]:
    # we don't actually have all the data we would need for 2011
    query = and_(
        Contract.player_id == Player.id,
        PlayerSeason.player_id == Player.id,
        Contract.start_year > 2011,
        Player.position != "",
    )
    stmt = select(Player).where(exists().where(query))
    for player in session.scalars(stmt).all():
        for csi in player.supporting_contract_info():
            if csi.contract_number > 1:
                yield csi


if __name__ == "__main__":
    expected_format: list[str] = []
    with get_session() as session:
        data: dict[tuple[int, int], dict] = {}
        for contract in get_all_contract_supporting_info(session):
            if contract.contract_number == 1:
                continue
            if contract.contract_season is None or contract.previous_season is None:
                continue
            if not data:
                expected_format = list((row := contract.to_scalar()))
            elif list(row := contract.to_scalar()) != expected_format:
                raise Exception(set(expected_format).symmetric_difference(row))
            data[contract.player.id, contract.season_id] = row

    df = DataFrame.from_dict(data, orient="index")
    df = df.sort_index()
    df.index.names = ["player_id", "season"]
    df.to_parquet("data/contracts-for-ml.parquet")
