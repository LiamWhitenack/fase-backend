import os
import time
from collections.abc import Iterable
from typing import Any

from pandas import DataFrame, Series, read_csv
from playwright.sync_api import sync_playwright
from sqlalchemy import select

from app.data.connection import get_session
from app.data.league.payroll import TeamPlayerSalary
from app.data.league.player import Player
from app.utils.math_utils import delay_seconds


def start_browser(AUTH_FILE: str, p: Any) -> tuple[Any, Any, Any]:
    browser = p.chromium.launch(headless=False)

    # Load or create context
    if os.path.exists(AUTH_FILE):
        print("Loading saved session…")
        context = browser.new_context(accept_downloads=True, storage_state=AUTH_FILE)
    else:
        print("No saved session found. You have 60 seconds to log in manually…")
        context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    return browser, context, page


def get_salary_data(
    page: Any,
    year: int,
    team_name: str,
    download_dir: str = "data/payroll-team-year",
) -> None:
    team_name = team_name.lower().replace(" ", "-")
    URL = f"https://www.spotrac.com/nba/{team_name}/cap/_/year/{year}"
    print(f"Visiting {URL}…")

    try:
        page.goto(URL, timeout=30000)
        page.wait_for_load_state("networkidle")
    except Exception as e:
        print(f"Could not load {URL}: {e}")
        return

    # Find all CSV buttons
    csv_buttons = page.locator("text=CSV")
    try:
        count = csv_buttons.count()
    except Exception as e:
        print(f"Could not find CSV buttons on {URL}: {e}")
        return

    print(f"Found {count} CSV buttons on the page.")

    for i in range(count):
        try:
            with page.expect_download() as download_info:
                csv_buttons.nth(i).click(timeout=10000)
            download = download_info.value

            # New filename
            new_filename = f"{team_name}-{year}-{i}.csv"
            save_path = os.path.join(download_dir, new_filename)

            # Save the download using the new name
            download.save_as(save_path)
            print(f"Downloaded {new_filename}")
        except Exception as e:
            print(f"Could not click CSV button {i + 1}: {e}")
            continue

        # Human-like delay between clicks
        delay_seconds(1, 2)
    delay_seconds(2, 2.5)


def get_all_salary_csvs() -> None:
    # Download folder
    DOWNLOAD_DIR = "data/payroll-team-year"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Path to save login/session info
    AUTH_FILE = "spotrac_auth.json"
    teams = read_csv("data/teams.csv", index_col=0)
    with sync_playwright() as p:
        # Launch browser
        browser, context, page = start_browser(AUTH_FILE, p)

        # Manual login if no session saved
        if not os.path.exists(AUTH_FILE):
            page.goto("https://www.spotrac.com", timeout=30000)
            print("Please log in manually in the browser window.")
            time.sleep(60)
            context.storage_state(path=AUTH_FILE)
            print(
                f"Session saved to {AUTH_FILE}. Next runs will use this login automatically."
            )

        # Iterate over years and teams
        for year in range(2027, 2032):
            for _, row in teams.iterrows():
                team_name: str = row["team_name"]
                if team_name == "los-angeles-clippers":
                    team_name = "la-clippers"
                get_salary_data(page, year, team_name, DOWNLOAD_DIR)

        print(f"Done! CSV files saved to: {os.path.abspath(DOWNLOAD_DIR)}")
        browser.close()


if __name__ == "__main__":
    get_all_salary_csvs()
