"""Graceful degradation between backends."""

from typing import List

from mqos.orchestration.backends import get_backend_status


def fallback_chain(prefer_hardware: bool = True) -> List[str]:
    """Return an ordered list of backends to try in sequence."""
    backends = get_backend_status()
    chain: List[str] = []

    if prefer_hardware:
        ibm = [
            name for name, info in backends.items()
            if info.get("provider") == "IBM Quantum" and info.get("status") == "online"
        ]
        chain.extend(sorted(ibm, key=lambda n: backends[n].get("pending_jobs", 0)))

    if "qiskit_aer" in backends:
        chain.append("qiskit_aer")

    return chain or ["qiskit_aer"]
