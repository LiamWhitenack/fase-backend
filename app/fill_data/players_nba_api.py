from __future__ import annotations

import time
from collections.abc import Iterable
from typing import Any

from nba_api.stats.endpoints.commonplayerinfo import CommonPlayerInfo
from nba_api.stats.static import players
from pandas import DataFrame

from app.data.league.player import Player
from app.utils.math_utils import delay_time


def height_to_inches(height: str | None) -> int | None:
    if not height:
        return None
    feet, inches = map(int, height.split("-"))
    return feet * 12 + inches


def player_from_api(data: dict[str, Any]) -> Player:
    """
    Convert a single CommonPlayerInfo-like dictionary to a Player instance.
    """
    # Map roster status to int: active=1, inactive=0
    if not (raw_status := data.get("ROSTERSTATUS")):
        roster_status = None
    if raw_status == "Active":
        roster_status = 1
    else:
        roster_status = 0

    # G League flag
    is_gleague_player = None
    gleague_flag = data.get("DLEAGUE_FLAG")
    if gleague_flag:
        is_gleague_player = gleague_flag.upper() == "Y"

    return Player(
        id=int(data["PERSON_ID"]),
        name=data.get("DISPLAY_FIRST_LAST"),
        first_name=data.get("FIRST_NAME"),
        last_name=data.get("LAST_NAME"),
        height_inches=height_to_inches(data.get("HEIGHT")),
        weight_pounds=int(data["WEIGHT"]) if data.get("WEIGHT") else None,
        birth_date=data.get("BIRTHDATE"),
        country=data.get("COUNTRY"),
        school=data.get("SCHOOL"),
        position=data.get("POSITION"),
        draft_year=int(data["DRAFT_YEAR"]) if data.get("DRAFT_YEAR") else None,
        draft_round=int(data["DRAFT_ROUND"]) if data.get("DRAFT_ROUND") else None,
        draft_number=int(data["DRAFT_NUMBER"]) if data.get("DRAFT_NUMBER") else None,
        roster_status=roster_status,
        is_gleague_player=is_gleague_player,
    )


def inspect_endpoint(endpoint: CommonPlayerInfo) -> dict[str, DataFrame]:
    result_sets: list[dict[str, Any]] = endpoint.get_dict()["resultSets"]
    pi = [d for d in result_sets if d["name"] == "CommonPlayerInfo"][0]

    return dict(zip(pi["headers"], pi["rowSet"][0]))


def get_all_player_ids(active_only: bool = False) -> list[int]:
    all_players = players.get_players()

    if active_only:
        all_players = [p for p in all_players if p["is_active"]]

    return [p["id"] for p in all_players]


def get_all_players() -> Iterable[Player]:
    for player_id in get_all_player_ids():
        try:
            endpoint = CommonPlayerInfo(player_id=player_id)
            yield player_from_api(inspect_endpoint(endpoint))
        except Exception as exc:
            print(f"Failed player_id={player_id}: {exc}")
        time.sleep(delay_time())
