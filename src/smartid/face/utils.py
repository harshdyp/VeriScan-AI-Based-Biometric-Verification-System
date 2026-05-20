from typing import Sequence
import numpy as np
from numpy.linalg import norm


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    a_arr = np.asarray(a, dtype=float)
    b_arr = np.asarray(b, dtype=float)
    denominator = norm(a_arr) * norm(b_arr)
    if denominator == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / denominator)


