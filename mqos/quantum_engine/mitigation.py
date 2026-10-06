"""Error mitigation — Zero-Noise Extrapolation."""

from typing import Dict, Any, List

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def apply_zne(
    circuit: QuantumCircuit,
    shots: int = 1024,
    scale_factors: List[float] = None,
) -> Dict[str, Any]:
    """Apply Zero-Noise Extrapolation to mitigate gate noise."""
    if scale_factors is None:
        scale_factors = [1.0, 1.5, 2.0]

    sim = AerSimulator()
    results = []

    for scale in scale_factors:
        scaled = _scale_circuit(circuit, scale)
        job = sim.run(transpile(scaled, sim), shots=shots)
        counts = job.result().get_counts()
        total = sum(counts.values())
        all_zero = "0" * circuit.num_qubits
        p0 = counts.get(all_zero, 0) / total if total else 0.0
        results.append({"scale": scale, "p0": p0})

    extrapolated = _linear_extrapolate(results)

    return {
        "raw_results": results,
        "extrapolated_value": round(extrapolated, 4),
        "mitigation_applied": True,
        "scale_factors": scale_factors,
    }


def _scale_circuit(circuit: QuantumCircuit, factor: float) -> QuantumCircuit:
    if factor <= 1.0:
        return circuit
    scaled = circuit.copy()
    extra = int((factor - 1.0) * circuit.depth())
    for _ in range(extra):
        for q in range(circuit.num_qubits):
            scaled.id(q)
    return scaled


def _linear_extrapolate(results: List[Dict[str, float]]) -> float:
    if len(results) < 2:
        return results[0]["p0"] if results else 0.0
    xs = [r["scale"] for r in results]
    ys = [r["p0"] for r in results]
    n = len(xs)
    sum_x = sum(xs)
    sum_y = sum(ys)
    sum_xy = sum(x * y for x, y in zip(xs, ys))
    sum_x2 = sum(x * x for x in xs)
    denom = n * sum_x2 - sum_x ** 2
    if denom == 0:
        return sum_y / n
    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n
    return intercept
