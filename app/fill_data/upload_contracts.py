import atexit
import json
import os
from collections.abc import Iterable
from datetime import datetime, timedelta
from difflib import get_close_matches

from pandas import DataFrame, Series, read_csv
from sqlalchemy import and_, select
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.data.connection import get_session
from app.data.league.payroll import TeamPlayerSalary
from app.data.league.player import Player
from app.data.league.team import Team


def get_salary_object(
    row: Series, team_id: int, player_id: int, year: int
) -> TeamPlayerSalary:
    def parse_dollars(value: str | None) -> int | None:
        if not value or value.strip() in {"'-", ""}:
            return None
        if value == "Two-Way":
            return None
        return int(value.replace("$", "").replace(",", ""))

    def parse_percent(value: str | None) -> float | None:
        if not value or value.strip() in {"'-", ""}:
            return None
        return float(value.replace("%", "").replace(",", ""))

    return TeamPlayerSalary(
        year=year,
        team_id=team_id,
        player_id=player_id,
        cap_hit_percent=parse_percent(
            row["Cap Hit Pct                         League Cap"]
        ),
        salary=parse_dollars(row["Cap Hit"]),
        apron_salary=parse_dollars(row.get("Apron Salary")),
        luxury_tax=parse_dollars(row.get("Luxury Tax")),
        cash_total=parse_dollars(row.get("Cash                         Total")),
        cash_garunteed=parse_dollars(
            row.get("Cash                         Guaranteed")
        ),
    )


def add_to_never_existed_list(name: str) -> None:
    with open("data/never-existed.json", "r") as f:
        res = json.load(f)
    res.append(name)
    with open("data/never-existed.json", "w") as f:
        res = json.dump(sorted(res), f, indent=4)


def add_to_existed_list(name: str) -> None:
    with open("data/confident-existed.json", "r") as f:
        res = json.load(f)
    res.append(name)
    with open("data/confident-existed.json", "w") as f:
        res = json.dump(sorted(res), f, indent=4)


class NameMatchFinder:
    def __init__(self) -> None:
        with get_session() as session:
            get = select(Player.id, Player.birth_date, Player.name)
            self.ids, self.bdays, self.names = tuple(zip(*session.execute(get).all()))
            self.bdays = list(map(datetime.fromisoformat, self.bdays))
            get = select(Team.name, Team.id)
            self.team_map: dict[str, int] = dict(session.execute(get).all())  # type: ignore
        with open("data/name-map.json") as f:
            self.data: dict[str, int | None] = json.load(f)

        atexit.register(self.save)

    def save(self) -> None:
        with open("data/name-map.json", "w") as f:
            json.dump(dict(sorted(self.data.items())), f, indent=4)

    def get_team(self, name: str) -> int:
        return self.team_map[name.replace("-", " ").title().replace("76Ers", "76ers")]

    def get_player_id(self, name: str, year: int, age: int | None) -> int | None:
        if name == "Nikola Milutinov":
            pass
        if name in self.data:
            return self.data[name]
        return self.guess_player_id(name, year, age)

    def guess_player_id(self, name: str, year: int, age: int | None) -> int | None:
        if sum([n == name for n in self.names]) == 1:
            self.data[name] = self.ids[self.names.index(name)]
        elif age is not None:
            bday_eligible_players = [
                player
                for player, bday in zip(self.names, self.bdays)
                if bday.year + age - 1 <= year < bday.year + age + 1
            ]
            similar_names = [
                player
                for player in bday_eligible_players
                if name.split(" ")[1] == (player.split(" ")[1] if " " in player else "")
            ]
            if similar_names:
                match = get_close_matches(name, similar_names, n=1, cutoff=0.0)[0]
            else:
                match = get_close_matches(name, self.names, n=1, cutoff=0.0)[0]
                remove = input(
                    f"Scary: matching {match} to {name}, add {name} to never existed?"
                )
                if remove == "y":
                    self.data[name] = None
                    return None

            self.data[name] = self.ids[self.names.index(match)]

        return self.data[name]


def get_all_salary_objects() -> Iterable[TeamPlayerSalary]:
    name_finder = NameMatchFinder()
    for file in sorted(os.listdir("data/payroll-team-year")):
        path = f"data/payroll-team-year/{file}"
        year = int(file[-10:-6])
        copy = file[-5]
        if copy != "0":
            continue
        team = file[:-11]
        df = read_csv(path)
        player_col: str = next(col for col in df if "Player" in col)  # type: ignore
        for _, row in df.iterrows():
            if (
                row["\xa0"] == "Incomplete Roster Charge"
                or row[player_col] != row[player_col]
                or "Round" in row[player_col]
            ):
                continue
            name = row[player_col].split("   ")[-1]
            if not (
                player_id := name_finder.get_player_id(
                    name,
                    year,
                    int(row["Age"]) if row["Age"] == row["Age"] else None,
                )
            ):
                continue
            yield get_salary_object(
                row,
                name_finder.get_team(team),
                player_id,
                year,
            )


def player_exists(session: Session, obj: TeamPlayerSalary) -> bool:
    res = session.execute(
        select(TeamPlayerSalary).where(
            and_(
                TeamPlayerSalary.team_id == obj.team_id,
                TeamPlayerSalary.player_id == obj.player_id,
                TeamPlayerSalary.year == obj.year,
            )
        )
    ).all()
    return len(res) > 0


if __name__ == "__main__":
    with get_session() as session:
        # session.query(Player).delete()
        for i, player in enumerate(get_all_salary_objects()):
            if player_exists(session, player):
                continue
            session.add(player)
            session.commit()
    pass
