"""
Environment-driven configuration for MQOS TERERAI.
"""

import os
from typing import List


class Config:
    """Runtime configuration container."""

    # IBM Quantum
    IBM_TOKEN: str = os.environ.get("IBM_QUANTUM_TOKEN", "")
    IBM_CRN: str = os.environ.get("IBM_QUANTUM_CRN", "")
    IBM_BACKEND: str = os.environ.get("IBM_QUANTUM_BACKEND", "ibm_kingston")
    IBM_CHANNEL: str = os.environ.get("IBM_QUANTUM_CHANNEL", "ibm_quantum_platform")

    # Security
    MQOS_SHARED_SECRET: str = os.environ.get("MQOS_SHARED_SECRET", "")
    ALLOWED_ORIGINS: List[str] = [
        o.strip()
        for o in os.environ.get(
            "ALLOWED_ORIGINS",
            "https://khensani-ai.onrender.com,"
            "https://luvuno-backend-proxy.onrender.com,"
            "http://localhost:3000,http://localhost:8000",
        ).split(",")
        if o.strip()
    ]

    # Cache
    CHSH_CACHE_TTL: int = int(os.environ.get("CHSH_CACHE_TTL", "3600"))

    # Keys
    KEY_ROTATION_DAYS: int = int(os.environ.get("KEY_ROTATION_DAYS", "30"))

    # Runtime
    PORT: int = int(os.environ.get("PORT", "8000"))

    @classmethod
    def ibm_configured(cls) -> bool:
        return bool(cls.IBM_TOKEN and cls.IBM_CRN)


config = Config()
