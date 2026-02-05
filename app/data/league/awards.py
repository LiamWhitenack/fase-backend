from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base

if TYPE_CHECKING:
    from app.data.league.season import Season


class Award(Base):
    __tablename__ = "awards"

    # ---- identifiers ----
    id: Mapped[int] = mapped_column(primary_key=True)

    # ---- award identity ----
    name: Mapped[str] = mapped_column(String, index=True)

    # Make season a foreign key
    season_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("seasons.id", ondelete="CASCADE"),  # <-- foreign key
        index=True,
        nullable=False,  # or True if some awards can have no season
    )

    # ---- recipient (one of these will be non-null) ----
    season: Mapped[Season] = relationship("Season")
    player_id: Mapped[int | None] = mapped_column(
        ForeignKey("players.id"), index=True, nullable=True
    )

    __table_args__ = (
        # Prevent duplicate awards for the same recipient in a season
        Index(
            "ix_award_unique_player",
            "name",
            "season_id",
            "player_id",
            unique=True,
        ),
    )
