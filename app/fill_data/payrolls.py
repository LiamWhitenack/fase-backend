import json
import os
from collections.abc import Iterable
from datetime import timedelta

from pandas import DataFrame, Series, read_csv
from sqlalchemy import and_, select
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.data.connection import get_session
from app.data.league.contract import Contract
from app.data.league.payroll import TeamPlayerBuyout, TeamPlayerSalary
from app.utils.name_matcher import NameMatchFinder


def get_salary_object(
    row: Series, team_id: int, player_id: int, year: int, buyout: bool
) -> TeamPlayerSalary | TeamPlayerBuyout:
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

    if buyout:
        return TeamPlayerBuyout(
            year=year + 1,
            team_id=team_id,
            player_id=player_id,
            salary=parse_dollars(row["Cap Hit"]),
        )

    return TeamPlayerSalary(
        year=year + 1,
        team_id=team_id,
        player_id=player_id,
        cap_hit_percent=parse_percent(
            row.get(
                "Cap Hit Pct                         League Cap",
                row.get("Cap Hit Pct                 League Cap"),
            )
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


def get_all_salary_objects() -> Iterable[TeamPlayerSalary | TeamPlayerBuyout]:
    name_finder = NameMatchFinder()

    def get_player_id(year: int, player_col: str, row: Series) -> int | None:
        if (
            row[player_col] == "Incomplete Roster Charge"
            or row[player_col] != row[player_col]
            or "Round" in row[player_col]
        ):
            return None
        name = row[player_col].split("   ")[-1].strip()
        if not (
            player_id := name_finder.get_player_id(
                name,
                year,
                int(row["Age"]) if row.get("Age", 0) == row.get("Age", 1) else None,
            )
        ):
            return None
        return player_id

    for file in sorted(os.listdir("data/payroll-team-year")):
        path = f"data/payroll-team-year/{file}"
        year = int(file[-10:-6])
        copy = file[-5]
        team = file[:-11]
        df = read_csv(path)
        if copy == "0":
            buyout = False
        elif " " in df.columns[1:]:
            continue
        else:
            buyout = True

        player_col: str = next(col for col in df if "Player" in col)  # type: ignore
        for _, row in df.iterrows():
            if player_id := get_player_id(year, player_col, row):
                yield get_salary_object(
                    row, name_finder.get_team(team), player_id, year, buyout
                )


def salary_exists(session: Session, obj: TeamPlayerSalary) -> bool:
    res = session.execute(
        select(TeamPlayerSalary).where(
            and_(
                TeamPlayerSalary.team_id == obj.team_id,
                TeamPlayerSalary.player_id == obj.player_id,
                TeamPlayerSalary.season == obj.season,
            )
        )
    ).all()
    return len(res) > 0


def buyout_exists(session: Session, obj: TeamPlayerBuyout) -> bool:
    res = session.execute(
        select(TeamPlayerBuyout).where(
            and_(
                TeamPlayerBuyout.team_id == obj.team_id,
                TeamPlayerBuyout.player_id == obj.player_id,
                TeamPlayerBuyout.season == obj.season,
            )
        )
    ).all()
    return len(res) > 0


def upload_payrolls(session: Session) -> None:
    # session.query(Player).delete()
    for i, player in enumerate(get_all_salary_objects()):
        if isinstance(player, TeamPlayerSalary) and salary_exists(session, player):
            continue
        if isinstance(player, TeamPlayerBuyout) and buyout_exists(session, player):
            continue
        session.add(player)
        session.commit()


if __name__ == "__main__":
    with get_session() as session:
        upload_payrolls(session)
    pass
