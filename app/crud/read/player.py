from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.league.player import Player


def get_player_by_id(session: Session, id: int) -> Player:
    return session.execute(select(Player).where(Player.id == id)).scalars().one()


def get_player_by_name(session: Session, name: str) -> Player:
    """Slower than getting by ID"""
    return session.execute(select(Player).where(Player.name == name)).scalars().one()
