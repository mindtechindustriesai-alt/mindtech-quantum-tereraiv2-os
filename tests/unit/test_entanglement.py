"""Unit tests for entanglement verification."""

from mqos.quantum_engine.chsh import compute_correlation


def test_perfect_correlated_bits():
    counts = {"00": 1000}
    assert compute_correlation(counts) == 1.0


def test_perfect_anticorrelated_bits():
    counts = {"01": 1000}
    assert compute_correlation(counts) == -1.0


def test_random_bits_give_zero_correlation():
    counts = {"00": 250, "01": 250, "10": 250, "11": 250}
    assert abs(compute_correlation(counts)) < 0.01
