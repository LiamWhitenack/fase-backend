import atexit
import json
from collections.abc import Callable
from contextlib import _GeneratorContextManager
from datetime import datetime
from difflib import get_close_matches

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.connection import get_session as get_dev_session
from app.data.league.player import Player
from app.data.league.team import Team


class NameMatchFinder:
    def __init__(
        self,
        get_session: Callable[..., _GeneratorContextManager[Session, None, None]]
        | None = None,
    ) -> None:
        if get_session is None:
            get_session = get_dev_session
        with get_session() as session:
            get = select(Player.id, Player.birth_date, Player.name)
            self.ids, self.bdays, self.names = tuple(zip(*session.execute(get).all()))
            self.bdays = list(map(datetime.fromisoformat, self.bdays))
            get = select(Team.name, Team.id)
            self.team_map: dict[str, int] = dict(session.execute(get).all())  # type: ignore
            get = select(Team.abbreviation, Team.id)
            self.team_abbr_map: dict[str, int] = dict(session.execute(get).all())  # type: ignore
        with open("data/name-map.json") as f:
            self.data: dict[str, int | None] = json.load(f)

        atexit.register(self.save)

    def save(self) -> None:
        with open("data/name-map.json", "w") as f:
            json.dump(dict(sorted(self.data.items())), f, indent=4)

    def get_team(self, name: str) -> int:
        if len(name) == 3:
            return self.team_abbr_map[name.replace("NOH", "NOP").replace("NJN", "BKN")]
        return self.team_map[name.replace("-", " ").title().replace("76Ers", "76ers")]

    def get_player_id(
        self, name: str, year: int, age: int | None, assume_match_exists: bool = False
    ) -> int | None:
        if name in self.data:
            return self.data[name]
        return self.guess_player_id(name, year, age, assume_match_exists)

    def guess_player_id(
        self, name: str, year: int, age: int | None, assume_match_exists: bool = False
    ) -> int | None:
        if sum([n == name for n in self.names]) == 1:
            self.data[name] = self.ids[self.names.index(name)]
        else:
            if age is not None:
                bday_eligible_players = [
                    player
                    for player, bday in zip(self.names, self.bdays)
                    if bday.year + age - 1 <= year < bday.year + age + 1
                ]
            else:
                bday_eligible_players = self.names
            similar_names = [
                player
                for player in bday_eligible_players
                if name.split(" ")[1] == (player.split(" ")[1] if " " in player else "")
            ]
            if similar_names:
                match = get_close_matches(name, similar_names, n=1, cutoff=0.0)[0]
            elif not assume_match_exists:
                match = get_close_matches(name, self.names, n=1, cutoff=0.0)[0]
                remove = input(
                    f"Scary: matching {match} to {name}, add {name} to never existed?"
                )
                if remove == "y":
                    self.data[name] = None
                    return None

            self.data[name] = self.ids[self.names.index(match)]

        self.save()
        return self.data[name]
