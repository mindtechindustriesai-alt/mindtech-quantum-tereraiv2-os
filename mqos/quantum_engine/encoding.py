"""Efficient data encoding — amplitude encoding."""

from typing import Dict, Any, List

import numpy as np
from qiskit import QuantumCircuit


def amplitude_encode(data: List[float]) -> Dict[str, Any]:
    """Encode N classical floats into log₂(N) qubits via amplitude encoding."""
    arr = np.array(data, dtype=float)
    if arr.size == 0:
        raise ValueError("Cannot encode empty data")

    norm = np.linalg.norm(arr)
    if norm == 0:
        norm = 1.0
    normalized = arr / norm

    padded_size = 2 ** int(np.ceil(np.log2(len(normalized))))
    padded = np.zeros(padded_size)
    padded[:len(normalized)] = normalized

    num_qubits = int(np.log2(padded_size))
    qc = QuantumCircuit(num_qubits)
    qc.initialize(padded, range(num_qubits))

    return {
        "circuit": qc,
        "num_qubits": num_qubits,
        "classical_size": len(data),
        "quantum_size": num_qubits,
        "compression_ratio": round(len(data) / num_qubits, 2) if num_qubits else 0.0,
        "normalized": normalized.tolist(),
    }
