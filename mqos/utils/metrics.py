"""Lightweight in-memory metrics (replace with Prometheus in future)."""

import time
from collections import defaultdict
from typing import Dict

_METRICS: Dict[str, int] = defaultdict(int)


def increment(name: str, amount: int = 1) -> None:
    _METRICS[name] += amount


def snapshot() -> Dict[str, int]:
    return dict(_METRICS)
