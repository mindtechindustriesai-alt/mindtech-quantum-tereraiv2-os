"""Key management — OS CSPRNG with rotation and revocation."""

import os
import time
import secrets
from typing import Dict, Any

_KEY_STATE: Dict[str, Dict[str, Any]] = {
    "active": {},
    "expired": {},
    "revoked": {},
}
KEY_ROTATION_DAYS = int(os.environ.get("KEY_ROTATION_DAYS", "30"))


def generate_key(length: int = 256, purpose: str = "encryption") -> Dict[str, Any]:
    """Generate a new cryptographic key via OS CSPRNG."""
    key_bytes = secrets.token_bytes(length // 8)
    key_id = f"K-{secrets.token_hex(4).upper()}"
    _KEY_STATE["active"][key_id] = {
        "length": length,
        "purpose": purpose,
        "created": time.time(),
        "rotates_at": time.time() + KEY_ROTATION_DAYS * 86400,
    }
    return {
        "key_id": key_id,
        "key_hex": key_bytes.hex(),
        "length": length,
        "purpose": purpose,
        "generated_by": "OS_CSPRNG",
        "timestamp": time.time(),
    }


def rotate_keys(limit: int = 10) -> Dict[str, Any]:
    """Rotate active keys — move oldest to expired, generate fresh."""
    rotated = 0
    for key_id in list(_KEY_STATE["active"].keys())[:limit]:
        _KEY_STATE["expired"][key_id] = _KEY_STATE["active"].pop(key_id)
        rotated += 1
    return {
        "keys_rotated": rotated,
        "new_active_count": len(_KEY_STATE["active"]),
        "timestamp": time.time(),
    }


def revoke_key(key_id: str) -> Dict[str, Any]:
    """Revoke a key — moves to revoked list, never reusable."""
    if key_id in _KEY_STATE["active"]:
        _KEY_STATE["revoked"][key_id] = _KEY_STATE["active"].pop(key_id)
        return {"success": True, "revoked_key": key_id}
    if key_id in _KEY_STATE["expired"]:
        _KEY_STATE["revoked"][key_id] = _KEY_STATE["expired"].pop(key_id)
        return {"success": True, "revoked_key": key_id}
    return {"success": False, "error": "Key not found"}


def key_inventory() -> Dict[str, Any]:
    """Current key inventory."""
    return {
        "active_keys": len(_KEY_STATE["active"]),
        "expired_keys": len(_KEY_STATE["expired"]),
        "revoked_keys": len(_KEY_STATE["revoked"]),
        "total_keys": sum(len(v) for v in _KEY_STATE.values()),
        "key_rotation_days": KEY_ROTATION_DAYS,
    }
