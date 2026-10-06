"""Unit tests for security subsystem."""

from mqos.security.keys import (
    generate_key, rotate_keys, revoke_key, key_inventory,
)


def test_generate_key_returns_hex():
    result = generate_key(length=256, purpose="test")
    assert result["length"] == 256
    assert len(result["key_hex"]) == 64


def test_inventory_counts_match():
    generate_key()
    inv = key_inventory()
    assert inv["active_keys"] >= 1


def test_rotate_keys_returns_count():
    rotate_keys(limit=1)
    result = rotate_keys(limit=1)
    assert "keys_rotated" in result


def test_revoke_nonexistent_key_fails():
    result = revoke_key("K-DOESNOTEXIST")
    assert result["success"] is False
