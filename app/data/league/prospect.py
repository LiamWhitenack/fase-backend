from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, timezone
from typing import Any

import bs4
from bs4 import BeautifulSoup
from sqlalchemy import (
    Date,
    DateTime,
    Float,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.base import Base


def safe_untyped_float(value: str | None) -> Any:
    if not value:
        return None
    try:
        return float(value.replace("%", "").strip())
    except ValueError:
        return None


def safe_untyped_int(value: str | None) -> Any:
    if not value:
        return None
    value = value.strip()
    if not value.isdigit():
        value = value[:-2]
    return int(value)


class DraftProspect(Base):
    __tablename__ = "draft_prospects"

    # -------------------------------------------------
    # Primary Key
    # -------------------------------------------------
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # -------------------------------------------------
    # Metadata
    # -------------------------------------------------
    date_uploaded: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # -------------------------------------------------
    # Profile / Identity
    # -------------------------------------------------
    name: Mapped[str | None] = mapped_column(String(128))
    tankathon_slug: Mapped[str | None] = mapped_column(
        String(128), unique=True, index=True
    )
    primary_position: Mapped[str | None] = mapped_column(String(2))
    secondary_position: Mapped[str | None] = mapped_column(String(2))
    height: Mapped[int | None] = mapped_column(Integer)
    weight: Mapped[int | None] = mapped_column(Integer)

    team: Mapped[str | None] = mapped_column(String(64))
    hometown: Mapped[str | None] = mapped_column(String(128))
    birthdate: Mapped[Date | None] = mapped_column(Date)

    tankathon_big_board_rank: Mapped[int | None] = mapped_column(Integer)
    espn_big_board_rank: Mapped[int | None] = mapped_column(Integer)
    year: Mapped[int | None] = mapped_column(Integer)
    age_at_draft: Mapped[Float | None] = mapped_column(Float)

    season: Mapped[int | None] = mapped_column(Integer, index=True)

    # -------------------------------------------------
    # Per Game Stats
    # -------------------------------------------------
    games: Mapped[int | None] = mapped_column(Integer)
    minutes_per_game: Mapped[Float | None] = mapped_column(Float)
    fgm: Mapped[Float | None] = mapped_column(Float)
    fga: Mapped[Float | None] = mapped_column(Float)
    fg_pct: Mapped[Float | None] = mapped_column(Float)
    tpm: Mapped[Float | None] = mapped_column(Float)
    tpa: Mapped[Float | None] = mapped_column(Float)
    three_pct: Mapped[Float | None] = mapped_column(Float)
    ftm: Mapped[Float | None] = mapped_column(Float)
    fta: Mapped[Float | None] = mapped_column(Float)
    ft_pct: Mapped[Float | None] = mapped_column(Float)
    rebounds: Mapped[Float | None] = mapped_column(Float)
    assists: Mapped[Float | None] = mapped_column(Float)
    steals: Mapped[Float | None] = mapped_column(Float)
    blocks: Mapped[Float | None] = mapped_column(Float)
    turnovers: Mapped[Float | None] = mapped_column(Float)
    fouls: Mapped[Float | None] = mapped_column(Float)
    points: Mapped[Float | None] = mapped_column(Float)

    # -------------------------------------------------
    # Per 36 Minutes Stats
    # -------------------------------------------------
    p36_fgm: Mapped[Float | None] = mapped_column(Float)
    p36_fga: Mapped[Float | None] = mapped_column(Float)
    p36_tpm: Mapped[Float | None] = mapped_column(Float)
    p36_tpa: Mapped[Float | None] = mapped_column(Float)
    p36_ftm: Mapped[Float | None] = mapped_column(Float)
    p36_fta: Mapped[Float | None] = mapped_column(Float)
    p36_rebounds: Mapped[Float | None] = mapped_column(Float)
    p36_assists: Mapped[Float | None] = mapped_column(Float)
    p36_steals: Mapped[Float | None] = mapped_column(Float)
    p36_blocks: Mapped[Float | None] = mapped_column(Float)
    p36_turnovers: Mapped[Float | None] = mapped_column(Float)
    p36_fouls: Mapped[Float | None] = mapped_column(Float)
    p36_points: Mapped[Float | None] = mapped_column(Float)

    # -------------------------------------------------
    # Advanced Stats Group I
    # -------------------------------------------------
    true_shooting_pct: Mapped[Float | None] = mapped_column(Float)
    effective_fg_pct: Mapped[Float | None] = mapped_column(Float)
    three_pa_rate: Mapped[Float | None] = mapped_column(Float)
    ft_rate: Mapped[Float | None] = mapped_column(Float)
    proj_nba_3p_pct: Mapped[Float | None] = mapped_column(Float)
    usage_pct: Mapped[Float | None] = mapped_column(Float)
    ast_to_usg: Mapped[Float | None] = mapped_column(Float)
    ast_to_to: Mapped[Float | None] = mapped_column(Float)

    # -------------------------------------------------
    # Advanced Stats Group II
    # -------------------------------------------------
    per_game_performance_rating: Mapped[Float | None] = mapped_column(
        Float
    )  # e.g., PER
    ows_per_40: Mapped[Float | None] = mapped_column(Float)
    dws_per_40: Mapped[Float | None] = mapped_column(Float)
    ws_per_40: Mapped[Float | None] = mapped_column(Float)
    offensive_rating: Mapped[Float | None] = mapped_column(Float)
    defensive_rating: Mapped[Float | None] = mapped_column(Float)
    offensive_bpm: Mapped[Float | None] = mapped_column(Float)
    defensive_bpm: Mapped[Float | None] = mapped_column(Float)
    bpm: Mapped[Float | None] = mapped_column(Float)

    @classmethod
    def from_beautiful_soup(
        cls,
        soup: BeautifulSoup,
        *,
        tankathon_slug: str | None = None,
    ) -> DraftProspect:
        data = cls()

        if tankathon_slug is not None:
            data.tankathon_slug = tankathon_slug

        label = soup.find("h1")
        if label:
            data.name = label.get_text(strip=True)

        data.update_summary_data(soup)

        table_methods: dict[str, Callable[[bs4.element.Tag], None]] = {
            "2025-26 PER GAME AVERAGES": data.parse_per_game_averages,
            "PER 36 MINUTES": data.parse_per_36_averages,
            "ADVANCED STATS I HOVER FOR DESCRIPTION TAP LABEL FOR DESCRIPTION": data.parse_advanced_stats_i,
            "ADVANCED STATS II HOVER FOR DESCRIPTION TAP LABEL FOR DESCRIPTION": data.parse_advanced_stats_ii,
        }

        for table, method in table_methods.items():
            for header_tag in soup.find_all(
                "div",
                class_="stats-header",
            ):
                sibling = header_tag.find_next_sibling("div", class_="stats")  # pyright: ignore[reportArgumentType]
                table_methods.get(header_tag.text, print)(sibling)

        return data
        # for cell in soup.select(
        #     "div.content div.stats div.stat-row div.stat-container"
        # ):
        #     label = row.find("div", class_="stat-label")
        #     value = row.find("div", class_="stat-data")
        #     if label is None or value is None:
        #         continue

        #     elif table_type == "Advanced":
        #         match label:
        #             case "TS%":
        #                 data["true_shooting_pct"] = safe_untyped_float(value)
        #             case "eFG%":
        #                 data["effective_fg_pct"] = safe_untyped_float(value)
        #             case "USG%":
        #                 data["usage_pct"] = safe_untyped_float(value)
        #             case "AST%":
        #                 data["assist_rate"] = safe_untyped_float(value)
        #             case "TOV%":
        #                 data["turnover_rate"] = safe_untyped_float(value)
        #             case "ORtg":
        #                 data["offensive_rating"] = safe_untyped_float(value)
        #             case "DRtg":
        #                 data["defensive_rating"] = safe_untyped_float(value)
        #             case "OBPM":
        #                 data["offensive_bpm"] = safe_untyped_float(value)
        #             case "DBPM":
        #                 data["defensive_bpm"] = safe_untyped_float(value)
        #             case "BPM":
        #                 data["bpm"] = safe_untyped_float(value)

        # return cls(**data)

    def update_summary_data(self, soup: bs4.BeautifulSoup) -> None:
        bio_table = soup.find("div", class_="player-info")
        if bio_table is None:
            print(f"No bio info for {self.name}!")
            return
        player_info_labels = bio_table.find_all("div", class_="label")
        player_info_values = bio_table.find_all("div", class_="data")
        data = dict(
            zip(
                (div.text for div in player_info_labels),
                (div.text for div in player_info_values),
            )
        )
        years = ["Freshman", "Sophomore", "Jnuior", "Senior"]
        self.team = data["Team"]
        self.high_school = data["High School"]
        self.year = years.index(data["Year"]) + 1
        if "/" in data["Position"]:
            self.primary_position, self.secondary_position = data["Position"].split("/")
        else:
            self.primary_position = data["Position"]
        self.height = int(data["Height"][0]) * 12 + int(data["Height"][2:-1])
        self.weight = safe_untyped_int(
            data["Weight"].replace("lbs", "").replace("lb", "").strip()
        )
        self.hometown = data["Hometown"]
        self.nation = data["Nation"].strip()
        self.birthdate = date.strptime(data["Birthdate"], "%b %d, %Y")  # type: ignore
        self.age_at_draft = safe_untyped_float(data["Age at Draft"][:-4])
        self.tankathon_big_board_rank = safe_untyped_int(data["Big Board"])
        self.espn_big_board_rank = safe_untyped_int(data["ESPN 100"].split(" |")[0][1:])

    def parse_per_game_averages(self, tag: bs4.element.Tag) -> None:
        stat_labels = [div.text for div in tag.find_all("div", class_="stat-label")]
        stat_data = [div.text for div in tag.find_all("div", class_="stat-data")]
        data = dict(zip(stat_labels, stat_data))
        self.games = safe_untyped_int(data["G"])
        self.minutes_per_game = safe_untyped_float(data["MP"])
        self.fgm, self.fga = map(safe_untyped_float, data["FGM-FGA"].split("-"))
        self.fg_pct = safe_untyped_float(data["FG%"])
        self.tpm, self.tpa = map(safe_untyped_float, data["3PM-3PA"].split("-"))
        self.three_pct = safe_untyped_float(data["3P%"])
        self.ftm, self.fta = map(safe_untyped_float, data["FTM-FTA"].split("-"))
        self.ft_pct = safe_untyped_float(data["FT%"])
        self.rebounds = safe_untyped_float(data["REB"])
        self.assists = safe_untyped_float(data["AST"])
        self.blocks = safe_untyped_float(data["BLK"])
        self.steals = safe_untyped_float(data["STL"])
        self.turnovers = safe_untyped_float(data["TO"])
        self.fouls = safe_untyped_float(data["PF"])
        self.points = safe_untyped_float(data["PTS"])

    def parse_per_36_averages(self, tag: bs4.element.Tag) -> None:
        stat_labels = [div.text for div in tag.find_all("div", class_="stat-label")]
        stat_data = [div.text for div in tag.find_all("div", class_="stat-data")]
        data = dict(zip(stat_labels, stat_data))
        self.p36_fgm, self.p36_fga = map(safe_untyped_float, data["FGM-FGA"].split("-"))
        self.p36_tpm, self.p36_tpa = map(safe_untyped_float, data["3PM-3PA"].split("-"))
        self.p36_ftm, self.p36_fta = map(safe_untyped_float, data["FTM-FTA"].split("-"))
        self.p36_rebounds = safe_untyped_float(data["REB"])
        self.p36_assists = safe_untyped_float(data["AST"])
        self.p36_blocks = safe_untyped_float(data["BLK"])
        self.p36_steals = safe_untyped_float(data["STL"])
        self.p36_turnovers = safe_untyped_float(data["TO"])
        self.p36_fouls = safe_untyped_float(data["PF"])
        self.p36_points = safe_untyped_float(data["PTS"])

    def parse_advanced_stats_i(self, tag: bs4.element.Tag) -> None:
        stat_labels = [div.text for div in tag.find_all("div", class_="stat-label")]
        stat_data = [div.text for div in tag.find_all("div", class_="stat-data")]
        data = dict(zip(stat_labels, stat_data))
        self.true_shooting_pct = safe_untyped_float(data["True Shooting %TS%"])
        self.effective_fg_pct = safe_untyped_float(data[r"Effective FG%EFG%"])
        self.three_pa_rate = safe_untyped_float(data["3PA Rate3PAR"])
        self.ft_rate = safe_untyped_float(data["FTA RateFTAR"])
        self.proj_nba_3p_pct = safe_untyped_float(data["Proj NBA 3P%NBA 3P%"])
        self.usage_pct = safe_untyped_float(data["USG%"])
        self.ast_to_usg = safe_untyped_float(data["AST/USG"])
        self.ast_to_to = safe_untyped_float(data["AST/TO"])

    def parse_advanced_stats_ii(self, tag: bs4.element.Tag) -> None:
        stat_labels = [div.text for div in tag.find_all("div", class_="stat-label")]
        stat_data = [div.text for div in tag.find_all("div", class_="stat-data")]
        data = dict(zip(stat_labels, stat_data))
        self.per_game_performance_rating = safe_untyped_float(data["PER"])
        self.ows_per_40 = safe_untyped_float(data["OWS/40"])
        self.dws_per_40 = safe_untyped_float(data["DWS/40"])
        self.ws_per_40 = safe_untyped_float(data["WS/40"])
        self.offensive_rating = safe_untyped_float(data["ORTG"])
        self.defensive_rating = safe_untyped_float(data["DRTG"])
        self.offensive_bpm = safe_untyped_float(data["OBPM"])
        self.defensive_bpm = safe_untyped_float(data["DBPM"])
        self.bpm = safe_untyped_float(data["BPM"])
