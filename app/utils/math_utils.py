from time import sleep

import numpy as np


def delay_seconds_count(mean: float = 5.0, scale: float = 1.0) -> float:
    return float(np.random.gamma(mean, scale))


def delay_seconds(mean: float = 5.0, var: float = 1.0) -> None:
    shape = mean**2 / var
    var = var / mean
    seconds = np.random.gamma(shape, var)
    print(f"delaying {round(seconds, 2)} seconds")
    sleep(seconds)
