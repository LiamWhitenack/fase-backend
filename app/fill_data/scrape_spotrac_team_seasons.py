#!/usr/bin/env python3
import os
import random
import time
from io import StringIO
from typing import Any

from pandas import DataFrame, read_html
from playwright.sync_api import sync_playwright

# ---------------- configuration ----------------

START_YEAR = 2011
END_YEAR = 2031  # inclusive
BASE_URL = "https://www.spotrac.com/nba/cap/_/year"
DATA_DIR = os.path.join("data", "cap-by-year")

# ---------------- utilities ----------------


def delay_seconds(mean: float = 4.0, var: float = 1.5) -> None:
    """Human-like delay using a gamma distribution."""
    shape = mean**2 / var
    scale = var / mean
    delay = random.gammavariate(shape, scale)
    time.sleep(round(delay, 2))


def normalize_money_columns(df: DataFrame) -> DataFrame:
    """
    Convert money-like columns ('$123,456,789') to floats.
    """
    for col in df.columns:
        if df[col].dtype == object and df[col].astype(str).str.contains(r"\$").any():
            df[col] = (
                df[col]
                .astype(str)
                .str.replace("$", "", regex=False)
                .str.replace(",", "", regex=False)
                .replace("", None)
                .astype(float)
            )
    return df


def get_cap_data_for_year(page: Any, year: int, output_dir: str) -> None:
    delay_seconds()
    url = f"{BASE_URL}/{year}"
    print(f"Visiting {url}")

    try:
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle")
    except Exception as exc:
        print(f"Failed to load {url}: {exc}")
        return

    delay_seconds()

    # Grab the fully rendered HTML
    html = page.content()

    try:
        read_html(StringIO(html))[1].to_csv(f"data/team-seasons/finances/{year}.csv")
    except Exception as exc:
        print(f"Failed to parse HTML for {year}: {exc}")
        return


# ---------------- main runner ----------------


def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        for year in range(START_YEAR, END_YEAR + 1):
            print(f"\n=== {year} NBA Cap ===")
            get_cap_data_for_year(page, year, DATA_DIR)

        browser.close()
        print("\nDone!")


if __name__ == "__main__":
    main()
