import pickle
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import requests
from bs4 import BeautifulSoup
from sqlalchemy import and_, select

from app.data.connection import get_session
from app.data.league.player import Player
from app.data.league.prospect import DraftProspect
from app.utils.math_utils import delay_seconds
from app.utils.name_matcher import NameMatchFinder


def get_soup(
    url: str = "https://www.tankathon.com/big_board", use_cache: bool = True
) -> BeautifulSoup:
    """
    Fetches the Tankathon Big Board page and returns a BeautifulSoup object.
    Optionally loads/saves the soup from/to a pickle file.
    """
    name = url.split(".com/")[-1].replace("/", "_")
    if use_cache and Path(f"{name}.pkl").exists():
        with Path(f"{name}.pkl").open("rb") as file:
            print("Loading BeautifulSoup from cache...")
            return pickle.load(file)

    print("Requesting page from Tankathon...")
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    if use_cache:
        with Path(f"{name}.pkl").open("wb") as file:
            pickle.dump(soup, file)
            print("Saved BeautifulSoup to cache.")

    return soup


def parse_big_board(soup: BeautifulSoup) -> tuple[datetime, set[str]]:
    """Extract rank and player link from the same row"""
    players: set[str] = set()

    # The table rows usually contain the rank and player link
    # Find all rows
    for a_tag in soup.find_all("a", class_="primary-hover"):
        players.add(a_tag["href"].split("/")[-1])  # pyright: ignore[reportAttributeAccessIssue]  # ty:ignore[possibly-missing-attribute]

    # Get last-updated timestamp
    dt_tag = soup.find("time")
    if dt_tag is None:
        raise Exception("No <time> tag found on page")

    return datetime.fromisoformat(dt_tag["datetime"]), players  # pyright: ignore[reportArgumentType]


def parse_tankathon_past_draft(soup: BeautifulSoup) -> set[str]:
    players: set[str] = set()

    # Each player seems to be inside a div with text like "Cooper Flagg SF/PF | Duke"
    for player_div in soup.find_all("a", class_="primary-hover"):
        if "players/" not in player_div["href"]:
            continue
        text = player_div["href"].split("/")[-1]  # type: ignore
        # Keep only the player name before the position
        players.add(text)

    return players


def fetch_player_page(slug: str) -> BeautifulSoup:
    url = f"https://www.tankathon.com/players/{slug}"
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def normalize_latin_letters(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    stripped = "".join(char for char in normalized if not unicodedata.combining(char))
    return stripped.lower()


if __name__ == "__main__":
    soup = get_soup()

    dt = datetime(2024, 4, 25, 20)
    soup = get_soup(f"https://www.tankathon.com/past_drafts/{dt.year}")
    draft = parse_tankathon_past_draft(soup)

    with get_session() as session:
        name_finder = NameMatchFinder()

        seen_players = set(
            s[0] for s in session.execute(select(DraftProspect.tankathon_slug)).all()
        )
        for player in draft:
            name = player.replace("-", " ").title()
            player_id = name_finder.get_player_id(name, 2024, age=None)
            actual_name = session.execute(
                select(Player.name).where(Player.id == player_id)
            ).first()
            if player_id is None or actual_name is None or actual_name[0] != name:
                continue
            if player in seen_players:
                continue
            print(player)
            session.add(
                DraftProspect.from_beautiful_soup(
                    dt,
                    fetch_player_page(player),
                    tankathon_slug=player,
                    year=dt.year,
                    player_id=player_id,
                )
            )
            session.commit()
            delay_seconds(30, 4)
