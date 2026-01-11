from typing import Any
from playwright.sync_api import sync_playwright
import os
import time
import numpy as np
from pandas import read_csv
from playwright.sync_api._context_manager import PlaywrightContextManager

# Load teams
teams = read_csv("data/teams.csv", index_col=0)

# Download folder
DOWNLOAD_DIR = os.path.join("data", "by-team")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Path to save login/session info
AUTH_FILE = "spotrac_auth.json"

# Gamma distribution parameters for human-like delays
GAMMA_SHAPE = 5.0  # k
GAMMA_SCALE = 1.0  # θ

# Safe navigation timeout (ms)
NAV_TIMEOUT = 30000  # 30 seconds
CLICK_TIMEOUT = 10000  # 10 seconds max for clicks

def start_browser(AUTH_FILE: str, p: Any) -> tuple[Any, Any, Any]:
    browser = p.chromium.launch(headless=False)

    # Load or create context
    if os.path.exists(AUTH_FILE):
        print("Loading saved session…")
        context = browser.new_context(
            accept_downloads=True,
            storage_state=AUTH_FILE
        )
    else:
        print("No saved session found. You have 60 seconds to log in manually…")
        context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    return browser, context, page

with sync_playwright() as p:
    # Launch browser
    browser, context, page = start_browser(AUTH_FILE, p)


    # Manual login if no session saved
    if not os.path.exists(AUTH_FILE):
        print("Please log in manually in the browser window.")
        time.sleep(60)
        context.storage_state(path=AUTH_FILE)
        print(f"Session saved to {AUTH_FILE}. Next runs will use this login automatically.")

    # Iterate over years and teams
    for year in range(2011, 2032):
        for _, row in teams.iterrows():
            # Human-like delay before visiting next page
            time.sleep(np.random.gamma(GAMMA_SHAPE, GAMMA_SCALE))

            team_name = row["team_name"].lower().replace(" ", "-")
            URL = f"https://www.spotrac.com/nba/{team_name}/overview/_/year/{year}"
            print(f"Visiting {URL}…")

            try:
                page.goto(URL, timeout=NAV_TIMEOUT)
                page.wait_for_load_state("networkidle")
            except Exception as e:
                print(f"Could not load {URL}: {e}")
                continue

            # Human-like delay after page load
            time.sleep(np.random.gamma(GAMMA_SHAPE, GAMMA_SCALE))

            # Find all CSV buttons
            csv_buttons = page.locator("text=CSV")
            try:
                count = csv_buttons.count()
            except Exception as e:
                print(f"Could not find CSV buttons on {URL}: {e}")
                continue

            print(f"Found {count} CSV buttons on the page.")

            for i in range(count):
                try:
                    with page.expect_download() as download_info:
                        csv_buttons.nth(i).click(timeout=CLICK_TIMEOUT)
                    download = download_info.value

                    # New filename
                    new_filename = f"{team_name}-{year}-{i}.csv"
                    save_path = os.path.join(DOWNLOAD_DIR, new_filename)

                    # Save the download using the new name
                    download.save_as(save_path)
                    print(f"Downloaded {new_filename}")
                except Exception as e:
                    print(f"Could not click CSV button {i+1}: {e}")
                    continue

                # Human-like delay between clicks
                time.sleep(np.random.gamma(GAMMA_SHAPE, GAMMA_SCALE))


    print(f"Done! CSV files saved to: {os.path.abspath(DOWNLOAD_DIR)}")
    browser.close()
