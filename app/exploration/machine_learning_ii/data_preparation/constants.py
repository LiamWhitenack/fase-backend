from __future__ import annotations

from pathlib import Path

TARGET_COL = "relative_dollars"
TIME_COL = "season"
POSITION_COL = "position"
DATA_PATH = Path("data/contracts-for-ml.csv")
OUTPUT_DIR = Path("documentation/report/plots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
