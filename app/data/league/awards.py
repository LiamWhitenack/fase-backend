from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base

from .player import Player
from .team import Team


class Award(Base):
    __tablename__ = "awards"

    # ---- identifiers ----
    id: Mapped[int] = mapped_column(primary_key=True)

    # ---- award identity ----
    name: Mapped[str] = mapped_column(String, index=True)
    season: Mapped[int] = mapped_column(Integer, index=True)

    # ---- recipient (one of these will be non-null) ----
    player_id: Mapped[int | None] = mapped_column(
        ForeignKey("players.id"), index=True, nullable=True
    )

    __table_args__ = (
        # Prevent duplicate awards for the same recipient in a season
        Index(
            "ix_award_unique_player",
            "name",
            "season",
            "player_id",
            unique=True,
        ),
    )
