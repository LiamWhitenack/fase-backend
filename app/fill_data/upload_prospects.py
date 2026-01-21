from datetime import datetime
from typing import Any

import joblib
import requests
from bs4 import BeautifulSoup

from app.data.connection import get_session
from app.data.league.prospect import DraftProspect


def fetch_player_page(slug: str) -> BeautifulSoup:
    url = f"https://www.tankathon.com/players/{slug}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


if __name__ == "__main__":
    soup = joblib.load("darryn-peterson.pkl")
    prospect = DraftProspect.from_beautiful_soup(
        soup,
        tankathon_slug="darryn-peterson",
    )
    with get_session() as session:
        session.add(prospect)
        session.commit()
