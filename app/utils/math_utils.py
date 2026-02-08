from time import sleep

import numpy as np
from tqdm import tqdm


def delay_seconds_count(mean: float = 5.0, scale: float = 1.0) -> float:
    return float(np.random.gamma(mean, scale))


def delay_seconds(shape: float = 5.0, scale: float = 1.0) -> None:
    seconds = np.random.gamma(shape, scale)
    print(f"Delaying {round(seconds, 2)} seconds, mean is {shape * scale}")

    # Show progress bar
    for _ in tqdm(range(int(seconds * 100)), desc="Waiting", ncols=70):
        sleep(0.01)
