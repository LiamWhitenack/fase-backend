from enum import Enum as PyEnum

from sqlalchemy import Enum, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base import Base
from .player import Player


# --- Python Enum for contract options ---
class ContractOption(PyEnum):
    Player = "Player"
    Team = "Team"


class Contract(Base):
    __tablename__ = "contracts"

    # ---- identifiers ----
    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)

    # ---- core contract info ----
    value: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # total value in dollars
    start_year: Mapped[int] = mapped_column(Integer, index=True)
    duration: Mapped[int] = mapped_column(Integer)  # number of years

    # ---- optional contract clauses ----
    option_1: Mapped[ContractOption | None] = mapped_column(
        Enum(ContractOption), nullable=True
    )
    option_2: Mapped[ContractOption | None] = mapped_column(
        Enum(ContractOption), nullable=True
    )
    option_1_value: Mapped[int] = mapped_column(Integer, default=0)
    option_2_value: Mapped[int] = mapped_column(Integer, default=0)

    # ---- relationships ----
    player: Mapped[Player] = relationship(argument="Player", back_populates="contracts")

    # ---- indexes ----
    __table_args__ = (Index("ix_contract_player_year", "player_id", "start_year"),)
