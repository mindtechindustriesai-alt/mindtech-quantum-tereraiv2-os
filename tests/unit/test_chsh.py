"""Unit tests for CHSH."""

import pytest
from mqos.quantum_engine.chsh import (
    build_chsh_circuit, compute_correlation, compute_chsh_s, run_chsh,
)


def test_build_circuit_structure():
    qc = build_chsh_circuit(0, 22.5)
    assert qc.num_qubits == 2


def test_correlation_zero_total():
    assert compute_correlation({}) == 0.0


def test_correlation_perfect_bell():
    counts = {"00": 512, "11": 512}
    e = compute_correlation(counts)
    assert abs(e - 1.0) < 0.01


def test_chsh_s_formula():
    correlations = [0.7071, -0.7071, 0.7071, 0.7071]
    s = compute_chsh_s(correlations)
    assert abs(s - 2.8284) < 0.01


def test_run_chsh_returns_S_at_or_below_tsirelson():
    result = run_chsh(shots=1024, force_fresh=True)
    assert "S" in result
    if result["S"] is not None:
        assert abs(result["S"]) <= 2.8285
