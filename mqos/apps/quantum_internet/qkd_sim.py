"""QKD simulation stub — BB84."""

from typing import Dict, Any


def simulate_bb84(key_length_bits: int = 1024) -> Dict[str, Any]:
    return {
        "key_length_bits": key_length_bits,
        "protocol": "BB84",
        "status": "available",
    }
