"""Unit tests for circuit compression."""

from mqos.quantum_engine.chsh import build_chsh_circuit
from mqos.quantum_engine.compression import compress_circuit


def test_compression_returns_metrics():
    qc = build_chsh_circuit(0, 45)
    result = compress_circuit(qc)
    assert "metrics" in result
    assert result["metrics"]["original_size"] > 0
    assert "size_reduction_percent" in result["metrics"]
