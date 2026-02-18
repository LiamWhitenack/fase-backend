import logging

from sqlalchemy import create_engine, exists, select
from sqlalchemy.orm import Session, sessionmaker

from app.base import Base
from app.custom_types import MLSafe
from app.data.connection import get_session
from app.data.league import Contract, Player

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

DATABASE_URL = (
    "postgresql+psycopg://athlete_user:athlete_password@localhost:6543/athlete_market"
)

engine = create_engine(
    DATABASE_URL, echo=False
)  # echo=True prints SQL queries for debugging

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
session = Session(engine)


input_data: list[list[MLSafe]] = []

stmt = select(Player).where(exists().where(Contract.player_id == Player.id))
count: int = 0
for player in session.scalars(stmt).all():
    if not player.draft_year:
        continue
    if player.name == f"Andrew Wiggins":
        pass
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
        print(player.name)
        count += 1

print(count)
