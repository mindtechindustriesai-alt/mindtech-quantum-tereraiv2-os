"""Live IBM Quantum backend registry."""

import os
import time
from typing import Dict, Any, List

try:
    from qiskit_ibm_runtime import QiskitRuntimeService
    IBM_RUNTIME_AVAILABLE = True
except ImportError:
    IBM_RUNTIME_AVAILABLE = False

IBM_TOKEN = os.environ.get("IBM_QUANTUM_TOKEN", "")
IBM_CRN = os.environ.get("IBM_QUANTUM_CRN", "")
IBM_CHANNEL = os.environ.get("IBM_QUANTUM_CHANNEL", "ibm_quantum_platform")

_CACHE: Dict[str, Any] = {"data": None, "timestamp": 0}
CACHE_TTL = 300


def get_backend_status() -> Dict[str, Any]:
    """Query live backend status. Cached for 5 minutes."""
    now = time.time()
    if _CACHE["data"] and (now - _CACHE["timestamp"]) < CACHE_TTL:
        return _CACHE["data"]

    status: Dict[str, Any] = {}

    if IBM_RUNTIME_AVAILABLE and IBM_TOKEN and IBM_CRN:
        try:
            service = QiskitRuntimeService(
                channel=IBM_CHANNEL,
                token=IBM_TOKEN,
                instance=IBM_CRN,
            )
            for b in service.backends():
                try:
                    bstatus = b.status()
                    status[b.name] = {
                        "status": "online" if bstatus.operational else "degraded",
                        "qubits": b.num_qubits,
                        "operational": bstatus.operational,
                        "pending_jobs": bstatus.pending_jobs,
                        "provider": "IBM Quantum",
                    }
                except Exception as e:
                    status[b.name] = {
                        "status": "error",
                        "error": str(e),
                        "provider": "IBM Quantum",
                    }
        except Exception as e:
            status["ibm_error"] = {
                "status": "error",
                "error": str(e),
                "provider": "IBM Quantum",
            }
    else:
        status["ibm_unconfigured"] = {
            "status": "not_configured",
            "note": "Set IBM_QUANTUM_TOKEN and IBM_QUANTUM_CRN to enable",
            "provider": "IBM Quantum",
        }

    status["qiskit_aer"] = {
        "status": "online",
        "qubits": "unlimited (simulator)",
        "operational": True,
        "provider": "Qiskit Aer",
    }

    _CACHE["data"] = status
    _CACHE["timestamp"] = now
    return status


def list_available_backends() -> List[str]:
    """Return names of all available backends."""
    return list(get_backend_status().keys())
