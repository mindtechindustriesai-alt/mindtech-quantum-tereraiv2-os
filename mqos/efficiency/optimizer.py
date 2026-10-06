"""Efficiency optimizer."""
def optimize_job(qubits: int, shots: int, backend: str, optimize: bool) -> dict:
    if not optimize:
        return {"original_qubits": qubits, "optimized_qubits": qubits,
                "original_shots": shots, "optimized_shots": shots,
                "circuit_compression": 0.0, "efficiency": 1.0}
    opt_qubits = max(1, int(qubits * 0.7))
    opt_shots = max(64, int(shots * 0.5))
    compression = 1 - (opt_qubits / qubits) if qubits else 0
    efficiency = min(0.99, 0.6 + compression)
    return {"original_qubits": qubits, "optimized_qubits": opt_qubits,
            "original_shots": shots, "optimized_shots": opt_shots,
            "circuit_compression": round(compression, 2),
            "efficiency": round(efficiency, 2)}
