import numpy as np


def delay_time(mean: float = 5.0, scale: float = 1.0) -> float:
    return float(np.random.gamma(mean, scale))
