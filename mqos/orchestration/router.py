"""Router — dynamic backend selection."""

from typing import Dict, Any
from mqos.orchestration.backends import get_backend_status


def select_backend(circuit_qubits: int, prefer_hardware: bool = False) -> str:
    backends = get_backend_status()
    candidates = []
    for name, info in backends.items():
        if info.get("status") != "online":
            continue
        if info.get("provider") == "Qiskit Aer":
            candidates.append({
                "name": name,
                "score": 100 if not prefer_hardware else 50,
                "qubits": float("inf"),
            })
        else:
            qubits = info.get("qubits", 0)
            if qubits >= circuit_qubits:
                score = 200 if prefer_hardware else 100
                score -= info.get("pending_jobs", 0) * 2
                candidates.append({
                    "name": name, "score": score, "qubits": qubits,
                })
    if not candidates:
        return "qiskit_aer"
    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates[0]["name"]


def route_circuit(circuit_qubits: int, shots: int = 1024, prefer_hardware: bool = False) -> Dict[str, Any]:
    backend = select_backend(circuit_qubits, prefer_hardware)
    backends = get_backend_status()
    return {
        "selected_backend": backend,
        "backend_info": backends.get(backend, {}),
        "rationale": {
            "circuit_qubits": circuit_qubits,
            "shots": shots,
            "prefer_hardware": prefer_hardware,
        },
    }
