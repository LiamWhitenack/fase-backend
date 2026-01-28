import pickle
import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, time
from pathlib import Path
from time import sleep
from typing import Any

import joblib
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry  # type: ignore[unreolved-import]
from sqlalchemy import and_, select
from sqlalchemy.orm.session import Session

from app.data.connection import get_session
from app.data.league.player import Player
from app.data.league.prospect import DraftProspect
from app.utils.math_utils import delay_seconds
from app.utils.name_matcher import NameMatchFinder


@dataclass
class DraftProspectParams:
    slug: str
    player_id: int | None = None


def get_soup(
    url: str = "https://www.tankathon.com/big_board", use_cache: bool = True
) -> BeautifulSoup:
    """
    Fetches the Tankathon Big Board page and returns a BeautifulSoup object.
    Optionally loads/saves the soup from/to a pickle file.
    """
    name = url.split(".com/")[-1].replace("/", "_")
    if use_cache and Path(f"pickles/{name}.pkl").exists():
        with Path(f"pickles/{name}.pkl").open("rb") as file:
            print("Loading BeautifulSoup from cache...")
            return pickle.load(file)

    print("Requesting page from Tankathon...")
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    if use_cache:
        with Path(f"pickles/{name}.pkl").open("wb") as file:
            pickle.dump(soup, file)
            print("Saved BeautifulSoup to cache.")

    return soup


def parse_tankathon_past_draft(
    session: Session,
    soup: BeautifulSoup,
    *,
    collect_only_missing: bool = True,
) -> list[DraftProspectParams]:
    slugs = get_slugs(soup)
    player_ids = get_player_ids_from_slugs(session, slugs)

    if collect_only_missing:
        stmt = select(DraftProspect.tankathon_slug)
        ignore_players = set(s[0] for s in session.execute(stmt).all())
    else:
        ignore_players = set()

    return [
        DraftProspectParams(n, p_id)
        for n, p_id in zip(slugs, player_ids)
        if n not in ignore_players
    ]


def parse_big_board(soup: BeautifulSoup) -> tuple[datetime, list[DraftProspectParams]]:
    players: set[str] = set()

    # The table rows usually contain the rank and player link
    # Find all rows
    for a_tag in soup.find_all("a", class_="primary-hover"):
        players.add(a_tag["href"].split("/")[-1])  # ty:ignore[possibly-missing-attribute]

    # Get last-updated timestamp
    dt_tag = soup.find("time")
    if dt_tag is None:
        raise Exception("No <time> tag found on page")

    return datetime.fromisoformat(dt_tag["datetime"]), [
        DraftProspectParams(p) for p in players
    ]


def fetch_player_page(slug: str) -> BeautifulSoup:
    url = f"https://www.tankathon.com/players/{slug}"

    # Set up session with retries
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # Number of retries
        backoff_factor=1,  # Wait 1s, 2s, 4s between retries
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)

    response = session.get(url, timeout=120)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def normalize_latin_letters(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    stripped = "".join(char for char in normalized if not unicodedata.combining(char))
    return stripped.lower()


def get_slugs(soup) -> list[str]:
    draft: set[str] = set()

    # Each player seems to be inside a div with text like "Cooper Flagg SF/PF | Duke"
    for player_div in soup.find_all("a", class_="primary-hover"):
        if "players/" not in player_div["href"]:
            continue
        text = player_div["href"].split("/")[-1]
        # Keep only the player name before the position
        draft.add(text)
    return list(draft)


def get_player_ids_from_slugs(session: Session, slugs: list[str]) -> list[int | None]:
    res: list[int | None] = []
    name_finder = NameMatchFinder()
    for slug in slugs:
        estimated_name = slug.replace("-", " ").title()
        player_id = name_finder.get_player_id(estimated_name, 2024, age=None)
        actual_name = session.execute(
            select(Player.name).where(Player.id == player_id)
        ).one_or_none()
        if player_id is None or actual_name is None or actual_name[0]:
            res.append(None)
        elif name := name_finder.get_player_id(actual_name[0], 2024, age=None):
            res.append(name)
        else:
            res.append(None)
    return res


def get_prospect_from_tankathon(
    dt: datetime, player_slug: str, player_id: int | None
) -> DraftProspect:
    return DraftProspect.from_beautiful_soup(
        dt,
        fetch_player_page(player_slug),
        tankathon_slug=player_slug,
        year=dt.year,
        player_id=player_id,
    )


def get_previous_year_params(
    session: Session, year: int, collect_only_missing: bool = True
) -> tuple[datetime, list[DraftProspectParams]]:
    dt = datetime(year, 6, 22, 19)
    soup = get_soup(f"https://www.tankathon.com/past_drafts/{dt.year}")
    return dt, parse_tankathon_past_draft(
        session, soup, collect_only_missing=collect_only_missing
    )


def upload_current_big_board() -> None:
    dt, big_board = parse_big_board(get_soup(use_cache=False))

    with get_session() as session:
        for params in big_board:
            if prospect_at_date_exists(session, dt, params.slug):
                continue
            session.add(get_prospect_from_tankathon(dt, params.slug, params.player_id))
            session.commit()
            delay_seconds(5, 12)


def prospect_at_date_exists(session: Session, dt: datetime, slug: str) -> bool:
    return bool(
        session.execute(
            select(DraftProspect).where(
                and_(
                    DraftProspect.uploaded == dt,
                    DraftProspect.tankathon_slug == slug,
                )
            )
        ).one_or_none()
    )


def upload_previous_draft(year: int, *, collect_only_missing: bool = True) -> bool:
    any_uploaded = False
    with get_session() as session:
        dt, paramss = get_previous_year_params(
            session, year, collect_only_missing=collect_only_missing
        )
        for params in paramss:
            any_uploaded = True
            session.add(get_prospect_from_tankathon(dt, params.slug, params.player_id))
            session.commit()
            delay_seconds(5, 12)
    return any_uploaded


if __name__ == "__main__":
    # for year in range(2020, 2026):
    #     upload_previous_draft(year, collect_only_missing=True)
    upload_current_big_board()
