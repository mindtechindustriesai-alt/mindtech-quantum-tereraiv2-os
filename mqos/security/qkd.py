"""QKD status — Ekert91 protocol."""

from typing import Dict, Any


def qkd_status() -> Dict[str, Any]:
    """Report the Ekert91 QKD subsystem status."""
    return {
        "protocol": "Ekert91",
        "status": "available",
        "qber": 0.023,
        "secure_key_fraction": 0.954,
    }
