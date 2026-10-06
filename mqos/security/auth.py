"""Service-to-service authentication helpers."""

import os
from typing import Optional
from fastapi import Header, HTTPException

MQOS_SHARED_SECRET = os.environ.get("MQOS_SHARED_SECRET", "")


def verify_shared_secret(x_mqos_key: Optional[str] = Header(default=None)) -> None:
    """Verify X-MQOS-Key header matches configured shared secret."""
    if MQOS_SHARED_SECRET and x_mqos_key != MQOS_SHARED_SECRET:
        raise HTTPException(status_code=401, detail="Invalid X-MQOS-Key")
