import os
from collections.abc import Iterable

import requests
from bs4 import BeautifulSoup
from bs4._typing import _SomeTags
from pandas import read_csv
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.data.connection import get_session
from app.data.league.contract import Contract
from app.fill_data.upload_payrolls import salary_exists
from app.utils.name_matcher import NameMatchFinder


def get_options_table() -> _SomeTags:
    url = "https://www.basketball-reference.com/contracts/players.html"

    # Request the HTML (some sites block non-browser agents)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    # Find the main contracts table
    table = soup.find("table")

    if not table:
        raise ValueError("Could not find the contracts table on page")

    tag = table.find("tbody")
    assert tag is not None
    return tag.find_all("tr")


def write_down_options() -> None:
    with open("data/options.csv", "w") as options_csv:
        options_csv.write("name,player,team\n")
        for row in get_options_table():
            try:
                player_name = str(row.find_all("a")[1].string)
            except IndexError:
                continue
            options_csv.write(
                f"{player_name}, {str(row).count('salary-pl')}, {str(row).count('salary-tm')}\n"
            )


def listpathdir(dir: str) -> Iterable[str]:
    for file in os.listdir(dir):
        yield os.path.join(dir, file)


def get_options() -> dict[int, tuple[int, int]]:
    res: dict[int, tuple[int, int]] = {}
    name_finder = NameMatchFinder()
    for _, row in read_csv("data/options.csv").iterrows():
        name = name_finder.get_player_id(row["name"], 2025, None)
        assert name is not None
        res[name] = row["player"], row["team"]
    return res


def get_all_contract_objects() -> Iterable[Contract]:
    def parse_dollars(value: str | None) -> int | None:
        if not value or value.strip() in {"'-", ""}:
            return None
        if value == "Two-Way":
            return None
        return int(value.replace("$", "").replace(",", ""))

    name_finder = NameMatchFinder()
    options = get_options()
    for year, df in enumerate(map(read_csv, listpathdir("data/contracts")), start=2011):
        for _, row in df.iterrows():
            if row["Yrs"] != row["Yrs"]:
                continue
            age = row["Age                     At Signing"]
            player_id = name_finder.get_player_id(
                row["Player"], year, age=int(age) if age == age else None
            )
            if player_id is None:
                continue
            player_options, team_options = options.get(player_id, (0, 0))
            option_1, option_2 = None, None
            if player_options > 0:
                option_1 = "Player"
            if player_options == 2:
                option_2 = "Player"
            if team_options > 0:
                option_1 = "Team"
            if team_options == 2:
                option_2 = "Team"
            team = row["Team                     Signed With"][:3]
            yield Contract(
                player_id=player_id,
                team_id=name_finder.get_team(team),
                value=parse_dollars(row["Value"])
                if row["Value"] == row["Value"]
                else None,
                start_year=year,
                duration=int(row["Yrs"]),
                option_1=option_1,
                option_2=option_2,
            )


def contract_exists(session: Session, obj: Contract) -> bool:
    res = session.execute(
        select(Contract).where(
            and_(
                Contract.id == obj.id,
                Contract.player_id == obj.player_id,
                Contract.team_id == obj.team_id,
            )
        )
    ).all()
    return len(res) > 0


if __name__ == "__main__":
    # write_down_options()
    with get_session() as session:
        # session.query(Player).delete()
        for i, contract in enumerate(get_all_contract_objects()):
            if contract_exists(session, contract):
                continue
            session.add(contract)
            session.commit()
