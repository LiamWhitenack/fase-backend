import pickle
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import requests
from bs4 import BeautifulSoup
from sqlalchemy import select

from app.data.connection import get_session
from app.data.league.prospect import DraftProspect
from app.utils.math_utils import delay_seconds


def get_soup(
    url: str = "https://www.tankathon.com/big_board", use_cache: bool = True
) -> BeautifulSoup:
    """
    Fetches the Tankathon Big Board page and returns a BeautifulSoup object.
    Optionally loads/saves the soup from/to a pickle file.
    """
    if use_cache and Path("tankathon_big_board_soup.pkl").exists():
        with Path("tankathon_big_board_soup.pkl").open("rb") as file:
            print("Loading BeautifulSoup from cache...")
            return pickle.load(file)

    print("Requesting page from Tankathon...")
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    if use_cache:
        with Path("tankathon_big_board_soup.pkl").open("wb") as file:
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


def fetch_player_page(slug: str) -> BeautifulSoup:
    url = f"https://www.tankathon.com/players/{slug}"
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


if __name__ == "__main__":
    soup = get_soup()

    dt, players = parse_big_board(soup)

    print("\nLast updated:")
    print(dt)

    with get_session() as session:
        seen_players = set(
            s[0] for s in session.execute(select(DraftProspect.tankathon_slug)).all()
        )
        for player in players:
            if player in seen_players:
                continue
            print(player)
            session.add(
                DraftProspect.from_beautiful_soup(
                    dt, fetch_player_page(player), tankathon_slug=player
                )
            )
            session.commit()
            delay_seconds(120, var=120)
