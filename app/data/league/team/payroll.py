from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Index, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base

if TYPE_CHECKING:
    from app.data.league.player import Player
    from app.data.league.season import Season


class TeamPlayerSalary(Base):
    __tablename__ = "team_player_salaries"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence("team_player_salaries_id_seq"),
        primary_key=True,
    )

    # ---- core fields ----
    season_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("seasons.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    cap_hit_percent: Mapped[int | None] = mapped_column(Float)
    salary: Mapped[int | None] = mapped_column(Integer)
    apron_salary: Mapped[int | None] = mapped_column(Integer)
    luxury_tax: Mapped[int | None] = mapped_column(Integer)
    cash_total: Mapped[int | None] = mapped_column(Integer)
    cash_garunteed: Mapped[int | None] = mapped_column(Integer)

    # ---- relationships ----
    season: Mapped[Season] = relationship("Season")
    player: Mapped[Player] = relationship("Player", back_populates="salaries")

    __table_args__ = (
        Index("ix_salary_unique", "season_id", "team_id", "player_id", unique=True),
    )

    def __repr__(self) -> str:
        return (
            f"<TeamPlayerSalary("
            f"id={self.id}, "
            f"season_id={self.season_id}, "
            f"team_id={self.team_id}, "
            f"player_id={self.player_id}, "
            f"salary={self.salary}, "
            f"cap_hit_percent={self.cap_hit_percent}"
            f")>"
        )

    @property
    def dollars(self) -> int:
        if self.salary is None:
            return 0
        return self.salary

    @property
    def relative_dollars(self) -> float:
        if self.salary is None:
            return 0.0
        return self.salary / self.season.cap


class TeamPlayerBuyout(Base):
    __tablename__ = "team_player_buyouts"

    # ---- primary key ----
    id: Mapped[int] = mapped_column(primary_key=True)

    # ---- core fields ----
    season_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("seasons.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    season: Mapped[Season] = relationship("Season")
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    salary: Mapped[int | None] = mapped_column(Integer)

    __table_args__ = (
        Index("ix_buyout_unique", "season_id", "team_id", "player_id", unique=True),
    )

    def __repr__(self) -> str:
        return (
            f"<TeamPlayerBuyout("
            f"id={self.id}, "
            f"season_id={self.season_id}, "
            f"team_id={self.team_id}, "
            f"player_id={self.player_id}, "
            f"salary={self.salary}"
            f")>"
        )

    @property
    def dollars(self) -> int:
        if self.salary is None:
            return 0
        return self.salary

    @property
    def relative_dollars(self) -> float:
        if self.salary is None:
            return 0.0
        return self.salary / self.season.cap
