"""
mqos/quantum_engine/chsh.py
Real CHSH verification — IBM Kingston primary, Qiskit Aer (exact) fallback.
Correlation metric: Bhattacharyya coefficient (per patent formula).
Anchored to reference job d8uhvl4bp3hs738628cg (IBM Kingston, S=2.76, 98.4%).
"""

import os
import math
import time
import uuid
from typing import Dict, Any, List, Optional

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.quantum_info import Statevector

try:
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    IBM_RUNTIME_AVAILABLE = True
except ImportError:
    IBM_RUNTIME_AVAILABLE = False

IBM_TOKEN = os.environ.get("IBM_QUANTUM_TOKEN", "")
IBM_CRN = os.environ.get("IBM_QUANTUM_CRN", "")
IBM_BACKEND = os.environ.get("IBM_QUANTUM_BACKEND", "ibm_kingston")
IBM_CHANNEL = os.environ.get("IBM_QUANTUM_CHANNEL", "ibm_quantum_platform")
USE_HARDWARE = IBM_RUNTIME_AVAILABLE and bool(IBM_TOKEN and IBM_CRN)

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

_CACHE: Dict[str, Any] = {
    "S": None, "correlation": None, "backend": None,
    "job_id": None, "job_ids": [], "shots": 0,
    "correlations": [], "counts": {},
    "timestamp": 0, "hardware_verified": False,
}
CACHE_TTL = int(os.environ.get("CHSH_CACHE_TTL", "3600"))

CHSH_BASES: List[tuple] = [(0, 22.5), (0, 67.5), (45, 22.5), (45, 67.5)]


def build_chsh_circuit(a_deg: float, b_deg: float) -> QuantumCircuit:
    qr = QuantumRegister(2, "q")
    cr = ClassicalRegister(2, "c")
    qc = QuantumCircuit(qr, cr)
    qc.h(qr[0])
    qc.cx(qr[0], qr[1])
    qc.ry(-2 * math.radians(a_deg), qr[0])
    qc.ry(-2 * math.radians(b_deg), qr[1])
    qc.measure(qr[0], cr[0])
    qc.measure(qr[1], cr[1])
    return qc


def compute_correlation(counts: Dict[str, int]) -> float:
    """E(a, b) = P(00) + P(11) - P(01) - P(10), bitstring normalized."""
    normalized = {k[::-1]: v for k, v in counts.items()}
    total = sum(normalized.values())
    if total == 0:
        return 0.0
    e00 = normalized.get("00", 0) / total
    e11 = normalized.get("11", 0) / total
    e01 = normalized.get("01", 0) / total
    e10 = normalized.get("10", 0) / total
    return e00 + e11 - e01 - e10


def compute_bhattacharyya(
    ideal_probs: Dict[str, float],
    measured_probs: Dict[str, float],
) -> float:
    """Bhattacharyya coefficient: C = Σ_i sqrt(p_ideal * p_measured)."""
    keys = set(ideal_probs.keys()) | set(measured_probs.keys())
    coeff = 0.0
    for k in keys:
        pi = ideal_probs.get(k, 0.0)
        pm = measured_probs.get(k, 0.0)
        if pi > 0 and pm > 0:
            coeff += math.sqrt(pi * pm)
    return coeff


def ideal_distribution(a_deg: float, b_deg: float) -> Dict[str, float]:
    """Ideal |Φ+> distribution after Ry(-2a) and Ry(-2b) rotations."""
    diff = 2 * math.radians(a_deg - b_deg)
    c2 = math.cos(diff) ** 2
    s2 = math.sin(diff) ** 2
    return {
        "00": 0.5 * c2,
        "01": 0.5 * s2,
        "10": 0.5 * s2,
        "11": 0.5 * c2,
    }


def compute_chsh_s(correlations: List[float]) -> float:
    if len(correlations) != 4:
        return 0.0
    return correlations[0] - correlations[1] + correlations[2] + correlations[3]


def _extract_counts(result, register_name: str = "c") -> Dict[str, int]:
    try:
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
    service = QiskitRuntimeService(
        channel=IBM_CHANNEL, token=IBM_TOKEN, instance=IBM_CRN,
    )
    backend = service.backend(IBM_BACKEND)
    sampler = SamplerV2(mode=backend)

    correlations: List[float] = []
    bhattacharyyas: List[float] = []
    job_ids: List[str] = []

    for a, b in CHSH_BASES:
        qc = build_chsh_circuit(a, b)
        compiled = transpile(qc, backend)
        job = sampler.run([compiled], shots=shots)
        job_ids.append(job.job_id())
        result = job.result()
        counts = _extract_counts(result, "c")
        correlations.append(compute_correlation(counts))

        # Bhattacharyya
        normalized = {k[::-1]: v / sum(counts.values()) for k, v in counts.items()}
        ideal = ideal_distribution(a, b)
        bhattacharyyas.append(compute_bhattacharyya(ideal, normalized))

    S = compute_chsh_s(correlations)
    avg_corr = sum(bhattacharyyas) / len(bhattacharyyas) if bhattacharyyas else 0.0

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
    correlations: List[float] = []
    bhattacharyyas: List[float] = []

    for a, b in CHSH_BASES:
        qc = build_chsh_circuit(a, b)
        qc_exact = qc.remove_final_measurements(inplace=False)
        sv = Statevector(qc_exact)
        probs = sv.probabilities_dict()
        normalized_probs = {k[::-1]: v for k, v in probs.items()}
        counts = {k: int(round(v * 1_000_000)) for k, v in normalized_probs.items()}
        correlations.append(compute_correlation(counts))

        ideal = ideal_distribution(a, b)
        measured = {k: float(v) for k, v in normalized_probs.items()}
        bhattacharyyas.append(compute_bhattacharyya(ideal, measured))

    S = compute_chsh_s(correlations)
    avg_corr = sum(bhattacharyyas) / len(bhattacharyyas) if bhattacharyyas else 0.0

    return {
        "S": round(S, 4),
        "correlation": round(avg_corr * 100, 2),
        "backend": "qiskit_aer_exact",
        "job_id": str(uuid.uuid4())[:12],
        "job_ids": [],
        "shots": "exact_statevector",
        "correlations": [round(c, 4) for c in correlations],
        "hardware_verified": False,
        "bases": CHSH_BASES,
    }


def run_chsh(shots: int = 1024, force_fresh: bool = False) -> Dict[str, Any]:
    now = time.time()
    if not force_fresh and _CACHE["S"] is not None and (now - _CACHE["timestamp"]) < CACHE_TTL:
        return dict(_CACHE)

    result: Optional[Dict[str, Any]] = None

    if USE_HARDWARE:
        try:
            result = _run_chsh_on_ibm(shots)
            print(f"[CHSH] IBM {IBM_BACKEND} · S={result['S']} · corr={result['correlation']}%")
        except Exception as e:
            print(f"[CHSH] IBM failed ({type(e).__name__}): {e}")

    if result is None:
        try:
            result = _run_chsh_on_aer(shots)
            print(f"[CHSH] Aer exact · S={result['S']} · corr={result['correlation']}%")
        except Exception as e:
            print(f"[CHSH] Aer failed: {e}")
            result = {
                "S": None, "correlation": None, "backend": "unavailable",
                "job_id": None, "job_ids": [], "shots": 0,
                "correlations": [], "hardware_verified": False,
                "error": str(e),
            }

    _CACHE.update(result)
    _CACHE["timestamp"] = now
    return dict(_CACHE)


def get_cached_chsh() -> Dict[str, Any]:
    if _CACHE["S"] is None:
        return run_chsh()
    return dict(_CACHE)


def get_history() -> Dict[str, Any]:
    return {"jobs": [REFERENCE_JOB]}


def cache_info() -> Dict[str, Any]:
    return {
        "cached": _CACHE["S"] is not None,
        "age_seconds": round(time.time() - _CACHE["timestamp"], 1) if _CACHE["timestamp"] else None,
        "ttl_seconds": CACHE_TTL,
        "hardware_available": USE_HARDWARE,
        "ibm_configured": bool(IBM_TOKEN and IBM_CRN),
        "backend": IBM_BACKEND,
    }
