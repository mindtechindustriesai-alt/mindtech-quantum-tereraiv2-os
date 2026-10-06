"""
MQOS TERERAI v2.1 — Africa's Quantum Operating System
MindTech Industries · SA Patent 2026/05142
"""

__version__ = "2.1.0"
__author__ = "MindTech Industries"
__patent__ = "SA 2026/05142"

from mqos.quantum_engine.chsh import (
    run_chsh, get_cached_chsh, get_history, cache_info,
)
from mqos.orchestration.backends import (
    get_backend_status, list_available_backends,
)
from mqos.orchestration.router import select_backend, route_circuit
from mqos.efficiency.optimizer import optimize_job
from mqos.security.keys import (
    key_inventory, generate_key, rotate_keys, revoke_key,
)
from mqos.security.qkd import qkd_status

__all__ = [
    "run_chsh", "get_cached_chsh", "get_history", "cache_info",
    "get_backend_status", "list_available_backends",
    "select_backend", "route_circuit",
    "optimize_job",
    "key_inventory", "generate_key", "rotate_keys", "revoke_key",
    "qkd_status",
]
