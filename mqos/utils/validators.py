"""Input validation helpers."""

def is_valid_qubit_count(qubits: int, max_qubits: int = 200) -> bool:
    return 1 <= qubits <= max_qubits


def is_valid_shots(shots: int, min_shots: int = 64, max_shots: int = 100_000) -> bool:
    return min_shots <= shots <= max_shots
