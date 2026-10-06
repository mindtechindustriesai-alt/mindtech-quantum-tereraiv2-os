"""MPS tensor network stub — bond dimension management."""

from typing import Dict, Any


def mps_info() -> Dict[str, Any]:
    return {
        "representation": "Matrix Product State",
        "bond_dimension": 64,
        "max_sites": 100,
    }
