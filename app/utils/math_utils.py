from time import sleep

import numpy as np


def delay_seconds_count(mean: float = 5.0, scale: float = 1.0) -> float:
    return float(np.random.gamma(mean, scale))


def delay_seconds(mean: float = 5.0, scale: float = 1.0) -> None:
    sleep(np.random.gamma(mean, scale))
