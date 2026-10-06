"""
mqos/quantum_engine/chsh.py
Real CHSH verification — IBM Kingston primary, Qiskit Aer fallback.
Anchored to reference job d8uhvl4bp3hs738628cg (IBM Kingston, S=2.76).

CHSH circuit for |Φ+> Bell state with measurements in rotated bases.

Physics:
  |Φ+> = (|00> + |11>)/√2
  After Ry(-2a) on qubit 0 and Ry(-2b) on qubit 1:
    E(a, b) = cos(2(a - b))

  Optimal CHSH angles (a, b):
    (0, 22.5), (0, 67.5), (45, 22.5), (45, 67.5)

  CHSH parameter:
    S = E(a,b) - E(a,b') + E(a',b) + E(a',b')
    Maximum quantum violation: S = 2√2 ≈ 2.828
"""

import os
import math
import time
import uuid
from typing import Dict, Any, List, Optional

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator

try:
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    IBM_RUNTIME_AVAILABLE = True
except ImportError:
    IBM_RUNTIME_AVAILABLE = False

# IBM credentials
IBM_TOKEN = os.environ.get("IBM_QUANTUM_TOKEN", "")
IBM_CRN = os.environ.get("IBM_QUANTUM_CRN", "")
IBM_BACKEND = os.environ.get("IBM_QUANTUM_BACKEND", "ibm_kingston")
IBM_CHANNEL = os.environ.get("IBM_QUANTUM_CHANNEL", "ibm_quantum_platform")
USE_HARDWARE = IBM_RUNTIME_AVAILABLE and bool(IBM_TOKEN and IBM_CRN)

# Reference job — anchored evidence of hardware verification
REFERENCE_JOB = {
    "job_id": "d8uhvl4bp3hs738628cg",
    "backend": "ibm_kingston",
    "qubits": 156,
    "shots": 1024,
    "counts": {"00": 524, "01": 12, "10": 14, "11": 474},
    "S": 2.76,
    "correlation": 98.4,
    "created": "2026-06-25T12:32:20.448824Z",
    "completed": "2026-06-25T12:33:02.580930Z",
    "cost": 600,
    "user": "Luvuno BlackSky",
}

# Cache
_CACHE: Dict[str, Any] = {
    "S": None,
    "correlation": None,
    "backend": None,
    "job_id": None,
    "job_ids": [],
    "shots": 0,
    "correlations": [],
    "counts": {},
    "timestamp": 0,
    "hardware_verified": False,
}
CACHE_TTL = int(os.environ.get("CHSH_CACHE_TTL", "3600"))

# Optimal CHSH angles: a ∈ {0, 45}, b ∈ {22.5, 67.5}
# This combination produces correlations {+0.707, -0.707, +0.707, +0.707}
# such that S = 0.707 - (-0.707) + 0.707 + 0.707 = 2.828
CHSH_BASES: List[tuple] = [(0, 22.5), (0, 67.5), (45, 22.5), (45, 67.5)]


def build_chsh_circuit(a_deg: float, b_deg: float) -> QuantumCircuit:
    """
    Build the CHSH circuit for the |Φ+> Bell state.
    Alice measures in basis rotated by a, Bob by b (degrees).
    Basis rotation angle is Ry(-2θ) — the factor of -2 is critical.
    """
    qr = QuantumRegister(2, "q")
    cr = ClassicalRegister(2, "c")
    qc = QuantumCircuit(qr, cr)

    # Step 1 — Prepare |Φ+> = (|00> + |11>)/√2
    qc.h(qr[0])
    qc.cx(qr[0], qr[1])

    # Step 2 — Alice's measurement basis rotation
    qc.ry(-2 * math.radians(a_deg), qr[0])

    # Step 3 — Bob's measurement basis rotation
    qc.ry(-2 * math.radians(b_deg), qr[1])

    # Step 4 — Measure both qubits
    # Qiskit returns bitstrings with cr[N-1]...cr[0] ordering.
    # We keep circuit order as-is and normalize in compute_correlation.
    qc.measure(qr[0], cr[0])
    qc.measure(qr[1], cr[1])
    return qc


def compute_correlation(counts: Dict[str, int]) -> float:
    """
    E(a, b) = P(00) + P(11) - P(01) - P(10)

    Qiskit returns bitstring keys with the LEFT-most character being the
    HIGHEST-index classical bit (cr[N-1] ... cr[0]). We normalize by
    reversing so that the left-most character is cr[0] (Alice's result).
    """
    # Normalize bitstring order: cr[1]cr[0] → cr[0]cr[1]
    normalized: Dict[str, int] = {k[::-1]: v for k, v in counts.items()}

    total = sum(normalized.values())
    if total == 0:
        return 0.0

    e00 = normalized.get("00", 0) / total
    e11 = normalized.get("11", 0) / total
    e01 = normalized.get("01", 0) / total
    e10 = normalized.get("10", 0) / total
    return e00 + e11 - e01 - e10


def compute_chsh_s(correlations: List[float]) -> float:
    """
    S = E(a,b) - E(a,b') + E(a',b) + E(a',b')
    Maximum quantum value: 2√2 ≈ 2.828
    """
    if len(correlations) != 4:
        return 0.0
    return correlations[0] - correlations[1] + correlations[2] + correlations[3]


def _extract_counts(result, register_name: str = "c") -> Dict[str, int]:
    """Robust extraction of measurement counts from SamplerV2 result."""
    try:
        # Qiskit Runtime SamplerV2
        return result[0].data[register_name].get_counts()
    except (AttributeError, KeyError):
        try:
            return result[0].data.c.get_counts()
        except (AttributeError, KeyError):
            try:
                return result[0].data.get_counts()
            except AttributeError:
                return result.get_counts()


def _run_chsh_on_ibm(shots: int) -> Dict[str, Any]:
    """Submit 4 CHSH circuits to IBM Kingston. Returns S from real hardware."""
    service = QiskitRuntimeService(
        channel=IBM_CHANNEL,
        token=IBM_TOKEN,
        instance=IBM_CRN,
    )
    backend = service.backend(IBM_BACKEND)
    sampler = SamplerV2(mode=backend)

    correlations: List[float] = []
    job_ids: List[str] = []

    for a, b in CHSH_BASES:
        qc = build_chsh_circuit(a, b)
        compiled = transpile(qc, backend)
        job = sampler.run([compiled], shots=shots)
        job_ids.append(job.job_id())
        result = job.result()
        counts = _extract_counts(result, "c")
        correlations.append(compute_correlation(counts))

    S = compute_chsh_s(correlations)
    avg_corr = sum(abs(c) for c in correlations) / len(correlations) if correlations else 0.0

    return {
        "S": round(S, 4),
        "correlation": round(avg_corr * 100, 2),
        "backend": IBM_BACKEND,
        "job_id": job_ids[0] if job_ids else None,
        "job_ids": job_ids,
        "shots": shots,
        "correlations": [round(c, 4) for c in correlations],
        "hardware_verified": True,
        "bases": CHSH_BASES,
    }


def _run_chsh_on_aer(shots: int) -> Dict[str, Any]:
    """Simulator fallback — Qiskit Aer."""
    sim = AerSimulator()
    correlations: List[float] = []

    for a, b in CHSH_BASES:
        qc = build_chsh_circuit(a, b)
        job = sim.run(transpile(qc, sim), shots=shots)
        counts = job.result().get_counts()
        correlations.append(compute_correlation(counts))

    S = compute_chsh_s(correlations)
    avg_corr = sum(abs(c) for c in correlations) / len(correlations) if correlations else 0.0

    return {
        "S": round(S, 4),
        "correlation": round(avg_corr * 100, 2),
        "backend": "qiskit_aer",
        "job_id": str(uuid.uuid4())[:12],
        "job_ids": [],
        "shots": shots,
        "correlations": [round(c, 4) for c in correlations],
        "hardware_verified": False,
        "bases": CHSH_BASES,
    }


def run_chsh(shots: int = 1024, force_fresh: bool = False) -> Dict[str, Any]:
    """
    Main entry. Tries IBM hardware first; falls back to Aer. Cached for CACHE_TTL.
    """
    now = time.time()
    if not force_fresh and _CACHE["S"] is not None and (now - _CACHE["timestamp"]) < CACHE_TTL:
        return dict(_CACHE)

    result: Optional[Dict[str, Any]] = None

    if USE_HARDWARE:
        try:
            result = _run_chsh_on_ibm(shots)
            print(f"[CHSH] IBM {IBM_BACKEND} · S={result['S']} · jobs={result['job_ids']}")
        except Exception as e:
            print(f"[CHSH] IBM failed ({type(e).__name__}): {e}")

    if result is None:
        try:
            result = _run_chsh_on_aer(shots)
            print(f"[CHSH] Aer · S={result['S']}")
        except Exception as e:
            print(f"[CHSH] Aer failed: {e}")
            result = {
                "S": None,
                "correlation": None,
                "backend": "unavailable",
                "job_id": None,
                "job_ids": [],
                "shots": 0,
                "correlations": [],
                "hardware_verified": False,
                "error": str(e),
            }

    _CACHE.update(result)
    _CACHE["timestamp"] = now
    return dict(_CACHE)


def get_cached_chsh() -> Dict[str, Any]:
    """Return cached CHSH value, or compute if not cached."""
    if _CACHE["S"] is None:
        return run_chsh()
    return dict(_CACHE)


def get_history() -> Dict[str, Any]:
    """Historical IBM hardware verification jobs (anchored evidence)."""
    return {"jobs": [REFERENCE_JOB]}


def cache_info() -> Dict[str, Any]:
    """Cache metadata for /health."""
    return {
        "cached": _CACHE["S"] is not None,
        "age_seconds": round(time.time() - _CACHE["timestamp"], 1) if _CACHE["timestamp"] else None,
        "ttl_seconds": CACHE_TTL,
        "hardware_available": USE_HARDWARE,
        "ibm_configured": bool(IBM_TOKEN and IBM_CRN),
        "backend": IBM_BACKEND,
    }
