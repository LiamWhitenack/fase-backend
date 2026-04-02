from pathlib import Path

import matplotlib.pyplot as plt

from app.exploration.machine_learning_ii.data_preparation.constants import OUTPUT_DIR


def to_filename(title: str) -> str:
    keep_characters = set("qwertyuiopasdfghjklzxcvbnm _-")
    kept = "".join([char for char in title.lower() if char in keep_characters])
    return kept.replace(" ", "-").replace("_", "-")


def save_figure(filename: str) -> Path:
    output_path = OUTPUT_DIR / filename
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    return output_path
