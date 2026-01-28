from collections.abc import Iterable
from time import sleep

import requests
from bs4 import BeautifulSoup
from bs4._typing import _SomeTags
from requests.adapters import HTTPAdapter
from sqlalchemy import and_, select
from sqlalchemy.orm import Session
from urllib3.util.retry import Retry

from app.data.connection import get_session
from app.data.league.awards import Award
from app.utils.name_matcher import NameMatchFinder

AWARD_PAGES: dict[str, str] = {
    "Most Valuable Player": "https://www.basketball-reference.com/awards/mvp.html",
    "Defensive Player of the Year": "https://www.basketball-reference.com/awards/dpoy.html",
    "Rookie of the Year": "https://www.basketball-reference.com/awards/roy.html",
    "Sixth Man of the Year": "https://www.basketball-reference.com/awards/smoy.html",
    "Most Improved Player": "https://www.basketball-reference.com/awards/mip.html",
}
ALL_NBA_PAGES: dict[str, str] = {
    "All-NBA": "https://www.basketball-reference.com/awards/all_league.html",
    "All-Defense": "https://www.basketball-reference.com/awards/all_defense.html",
    "All-Rookie": "https://www.basketball-reference.com/awards/all_rookie.html",
}


# -----------------------
# requests session setup
# -----------------------

SESSION = requests.Session()

SESSION.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.basketball-reference.com/",
    }
)

retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)

SESSION.mount("https://", HTTPAdapter(max_retries=retries))


def get_award_rows(url: str) -> _SomeTags:
    response = SESSION.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    table = soup.find("table")

    if not table:
        raise ValueError(f"Could not find awards table for {url}")

    body = table.find("tbody")
    assert body is not None

    # Be polite — Basketball-Reference WILL block you otherwise
    sleep(5)

    return body.find_all("tr")


def parse_season(season_str: str) -> int:
    """
    Basketball-Reference uses '2023-24' → return 2024
    """
    try:
        return int(season_str.split("-")[0]) + 1
    except Exception:
        raise ValueError(f"Could not parse season: {season_str}")


def get_all_award_objects() -> Iterable[Award]:
    name_finder = NameMatchFinder()

    for award_name, url in AWARD_PAGES.items():
        for row in get_award_rows(url):
            if row.get("class") and "thead" in row["class"]:
                continue

            season_cell = row.find("th")
            if not season_cell:
                continue

            season = parse_season(season_cell.text.strip())

            player_link = row.find("a")
            if not player_link:
                continue

            player_name: str = row.find_all("a")[2].string  # type: ignore

            player_id = name_finder.get_player_id(
                player_name,
                season,
                None,
            )

            if player_id is None:
                continue

            yield Award(
                name=award_name,
                season=season,
                player_id=player_id,
            )

    for award_name, url in ALL_NBA_PAGES.items():
        for row in get_award_rows(url):
            if row.get("class") and "thead" in row["class"]:
                continue

            season_cell = row.find("th")
            if not season_cell:
                continue

            if row.find_all("a")[1].text != "NBA":
                continue

            season = parse_season(season_cell.text.strip())
            team_n = row.find_all()[4].text
            for name in row.find_all("a")[3:8]:
                player_id = name_finder.get_player_id(
                    name.text,
                    season,
                    None,
                    assume_match_exists=True,
                )
                assert player_id
                yield Award(
                    name=f"{team_n} Team {award_name}",
                    season=season,
                    player_id=player_id,
                )


def award_exists(session: Session, award: Award) -> bool:
    res = session.execute(
        select(Award).where(
            and_(
                Award.name == award.name,
                Award.season == award.season,
                Award.player_id == award.player_id,
            )
        )
    ).first()
    return res is not None


def upload_awards(session: Session) -> None:
    for award in get_all_award_objects():
        if award_exists(session, award):
            continue
        session.add(award)
        session.commit()


if __name__ == "__main__":
    with get_session() as session:
        upload_awards(session)
