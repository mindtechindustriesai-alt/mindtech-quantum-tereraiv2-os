"""Composite safety score — 40/30/20/10 weighting."""

from typing import Dict, Any

WEIGHTS = {"location": 0.40, "attendance": 0.30, "alerts": 0.20, "battery": 0.10}


def compute_composite_safety_score(
    location: float = 100.0,
    attendance: float = 100.0,
    alerts: float = 100.0,
    battery: float = 100.0,
) -> Dict[str, Any]:
    composite = (
        location * WEIGHTS["location"] +
        attendance * WEIGHTS["attendance"] +
        alerts * WEIGHTS["alerts"] +
        battery * WEIGHTS["battery"]
    )
    if composite >= 95:
        label = "Excellent"
    elif composite >= 85:
        label = "Good"
    else:
        label = "Needs Attention"
    return {
        "composite": round(composite, 1),
        "breakdown": {
            "location": round(location),
            "attendance": round(attendance),
            "alerts": round(alerts),
            "battery": round(battery),
        },
        "label": label,
    }
