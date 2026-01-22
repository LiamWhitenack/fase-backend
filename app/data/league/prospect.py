from __future__ import annotations

import re
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
    UniqueConstraint,
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


def parse_measurements(text: str) -> tuple[float | None, float | None]:
    """
    Parses a string like '6\'1.5" (6\'5.5" wingspan)' and returns height and wingspan in inches.
    """
    # Regex to match feet, inches (with optional decimal)
    if not text:
        return None, None
    pattern = r"(\d+)\'(\d+(?:\.\d+)?)\""

    matches = re.findall(pattern, text)

    if not matches:
        raise ValueError(f"Could not parse height/wingspan from '{text}'")

    # First match is height
    height_ft, height_in = matches[0]
    height_in_total = int(height_ft) * 12 + float(height_in)

    # Second match (if present) is wingspan
    if len(matches) > 1:
        wingspan_ft, wingspan_in = matches[1]
        wingspan_in_total = int(wingspan_ft) * 12 + float(wingspan_in)
    else:
        wingspan_in_total = None  # wingspan missing

    return height_in_total, wingspan_in_total


class DraftProspect(Base):
    __tablename__ = "draft_prospects"

    __table_args__ = (
        UniqueConstraint("name", "uploaded", name="uq_draft_prospect_name_uploaded"),
    )

    # -------------------------------------------------
    # Primary Key
    # -------------------------------------------------
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # -------------------------------------------------
    # Metadata
    # -------------------------------------------------
    uploaded: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # -------------------------------------------------
    # Profile / Identity
    # -------------------------------------------------
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    tankathon_slug: Mapped[str | None] = mapped_column(String(128))
    primary_position: Mapped[str | None] = mapped_column(String(2))
    secondary_position: Mapped[str | None] = mapped_column(String(2))
    height: Mapped[float | None] = mapped_column(Float)
    wingspan: Mapped[float | None] = mapped_column(Float)
    weight: Mapped[int | None] = mapped_column(Integer)

    team: Mapped[str | None] = mapped_column(String(64))
    hometown: Mapped[str | None] = mapped_column(String(128))
    birthdate: Mapped[Date | None] = mapped_column(Date)

    tankathon_big_board_rank: Mapped[int | None] = mapped_column(Integer)
    espn_big_board_rank: Mapped[int | None] = mapped_column(Integer)
    year: Mapped[int | None] = mapped_column(Integer)
    age_at_draft: Mapped[Float | None] = mapped_column(Float)

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
        uploaded: datetime,
        soup: BeautifulSoup,
        *,
        tankathon_slug: str | None = None,
    ) -> DraftProspect:
        data = cls(uploaded=uploaded)

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
                table_methods.get(header_tag.text, print)(sibling)  # pyright: ignore[reportArgumentType]

        return data

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
        years = ["Freshman", "Sophomore", "Junior", "Senior"]
        self.team = data["Team"]
        self.high_school = data.get("High School")
        self.year = years.index(data["Year"]) + 1 if data["Year"] in years else None
        if "/" in data["Position"]:
            self.primary_position, self.secondary_position = data["Position"].split("/")
        else:
            self.primary_position = data["Position"]
        self.height, self.wingspan = parse_measurements(data.get("Height", ""))
        self.weight = safe_untyped_int(
            data["Weight"].replace("lbs", "").replace("lb", "").strip()
        )
        self.hometown = data["Hometown"]
        self.nation = data["Nation"].strip()
        self.birthdate = date.strptime(data["Birthdate"], "%b %d, %Y")  # type: ignore
        self.age_at_draft = safe_untyped_float(data["Age at Draft"][:-4])
        self.tankathon_big_board_rank = safe_untyped_int(data["Big Board"])
        self.espn_big_board_rank = safe_untyped_int(
            data.get("ESPN 100", "").split(" |")[0][1:]
        )

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
        self.true_shooting_pct = safe_untyped_float(data.get("True Shooting %TS%"))
        self.effective_fg_pct = safe_untyped_float(data.get(r"Effective FG%EFG%"))
        self.three_pa_rate = safe_untyped_float(data.get("3PA Rate3PAR"))
        self.ft_rate = safe_untyped_float(data.get("FTA RateFTAR"))
        self.proj_nba_3p_pct = safe_untyped_float(data.get("Proj NBA 3P%NBA 3P%"))
        self.usage_pct = safe_untyped_float(data.get("USG%"))
        self.ast_to_usg = safe_untyped_float(data.get("AST/USG"))
        self.ast_to_to = safe_untyped_float(data.get("AST/TO"))

    def parse_advanced_stats_ii(self, tag: bs4.element.Tag) -> None:
        stat_labels = [div.text for div in tag.find_all("div", class_="stat-label")]
        stat_data = [div.text for div in tag.find_all("div", class_="stat-data")]
        data = dict(zip(stat_labels, stat_data))
        self.per_game_performance_rating = safe_untyped_float(data.get("PER"))
        self.ows_per_40 = safe_untyped_float(data.get("OWS/40"))
        self.dws_per_40 = safe_untyped_float(data.get("DWS/40"))
        self.ws_per_40 = safe_untyped_float(data.get("WS/40"))
        self.offensive_rating = safe_untyped_float(data.get("ORTG"))
        self.defensive_rating = safe_untyped_float(data.get("DRTG"))
        self.offensive_bpm = safe_untyped_float(data.get("OBPM"))
        self.defensive_bpm = safe_untyped_float(data.get("DBPM"))
        self.bpm = safe_untyped_float(data.get("BPM"))
