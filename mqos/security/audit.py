"""Immutable audit log (in-memory ring buffer for now)."""

import time
from collections import deque
from typing import Dict, Any, List

_AUDIT_LOG: deque = deque(maxlen=10_000)


def log_event(event_type: str, actor: str = "system", detail: Dict[str, Any] = None) -> None:
    """Append an immutable event to the audit log."""
    _AUDIT_LOG.append({
        "timestamp": time.time(),
        "event_type": event_type,
        "actor": actor,
        "detail": detail or {},
    })


def recent_events(limit: int = 100) -> List[Dict[str, Any]]:
    """Return the most recent audit events."""
    return list(_AUDIT_LOG)[-limit:]
