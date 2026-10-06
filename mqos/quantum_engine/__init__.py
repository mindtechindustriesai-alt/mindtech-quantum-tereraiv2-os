"""Quantum engine — circuits, compression, mitigation, encoding."""

from mqos.quantum_engine.chsh import (
    run_chsh, get_cached_chsh, get_history, cache_info,
    build_chsh_circuit, compute_correlation, compute_chsh_s,
)
from mqos.quantum_engine.compression import compress_circuit
from mqos.quantum_engine.mitigation import apply_zne
from mqos.quantum_engine.encoding import amplitude_encode

__all__ = [
    "run_chsh", "get_cached_chsh", "get_history", "cache_info",
    "build_chsh_circuit", "compute_correlation", "compute_chsh_s",
    "compress_circuit",
    "apply_zne",
    "amplitude_encode",
]
