"""QKD status — Ekert91 protocol."""
def qkd_status() -> dict:
    return {"protocol": "Ekert91", "status": "available",
            "qber": 0.023, "secure_key_fraction": 0.954}
