from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base import Base

if TYPE_CHECKING:
    from .player import Player
    from .team import Team


class TeamPlayerSalary(Base):
    __tablename__ = "team_player_salaries"

    # ---- primary key ----
    id: Mapped[int] = mapped_column(primary_key=True)

    # ---- core fields ----
    year: Mapped[int] = mapped_column(Integer, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    salary: Mapped[int] = mapped_column(Integer)

    # ---- relationships ----
    player: Mapped["Player"] = relationship("Player", back_populates="salaries")

    __table_args__ = (
        # Ensure uniqueness per player per team per year
        Index("ix_salary_unique", "year", "team_id", "player_id", unique=True),
    )


class TeamPlayerBuyout(Base):
    __tablename__ = "team_player_buyouts"

    # ---- primary key ----
    id: Mapped[int] = mapped_column(primary_key=True)

    # ---- core fields ----
    year: Mapped[int] = mapped_column(Integer, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    salary: Mapped[int] = mapped_column(Integer)

    __table_args__ = (
        # Ensure uniqueness per player per team per year
        Index("ix_buyout_unique", "year", "team_id", "player_id", unique=True),
    )
