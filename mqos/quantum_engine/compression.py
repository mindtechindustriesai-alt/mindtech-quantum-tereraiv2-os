"""Circuit compression — reduce gate and qubit requirements."""

from typing import Dict, Any

from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import (
    Optimize1qGatesDecomposition,
    CXCancellation,
    CommutativeCancellation,
)


def compress_circuit(circuit: QuantumCircuit, optimization_level: int = 3) -> Dict[str, Any]:
    """Compress a quantum circuit, returning metrics and the compressed circuit."""
    original_ops = circuit.count_ops()
    original_depth = circuit.depth()
    original_size = circuit.size()

    pass_manager = PassManager([
        CXCancellation(),
        CommutativeCancellation(),
        Optimize1qGatesDecomposition(),
    ])

    compressed = pass_manager.run(circuit)
    compressed = transpile(compressed, optimization_level=optimization_level)

    new_depth = compressed.depth()
    new_size = compressed.size()

    return {
        "circuit": compressed,
        "metrics": {
            "original_depth": original_depth,
            "compressed_depth": new_depth,
            "depth_reduction_percent": round(
                (1 - new_depth / original_depth) * 100, 2
            ) if original_depth > 0 else 0.0,
            "original_size": original_size,
            "compressed_size": new_size,
            "size_reduction_percent": round(
                (1 - new_size / original_size) * 100, 2
            ) if original_size > 0 else 0.0,
            "original_ops": dict(original_ops),
            "compressed_ops": dict(compressed.count_ops()),
        },
    }
