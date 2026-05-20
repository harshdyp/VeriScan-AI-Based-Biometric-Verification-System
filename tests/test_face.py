import numpy as np
from smartid.face.utils import cosine_similarity


def test_cosine_similarity_basic():
    a = np.array([1.0, 0.0])
    b = np.array([1.0, 0.0])
    assert cosine_similarity(a, b) == 1.0


def test_cosine_similarity_orthogonal():
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 1.0])
    assert abs(cosine_similarity(a, b)) < 1e-9


def test_cosine_similarity_zero_vector():
    a = np.array([0.0, 0.0])
    b = np.array([1.0, 2.0])
    assert cosine_similarity(a, b) == 0.0


