"""TrumpProof Core Module

CLAUDEME-compliant foundation. Every other file imports this.
Contains: dual_hash, emit_receipt, merkle, StopRule

No receipt → not real.
"""

import hashlib
import json
from datetime import datetime

try:
    import blake3

    HAS_BLAKE3 = True
except ImportError:
    HAS_BLAKE3 = False

# === TENANT ===
TENANT_ID = "trumpproof"

# === RECEIPT SCHEMA ===
RECEIPT_SCHEMA = {
    "receipt_type": "str",
    "ts": "ISO8601",
    "tenant_id": "str",
    "payload_hash": "str",  # SHA256:BLAKE3 format
}


class StopRule(Exception):
    """Raised when stoprule triggers. Never catch silently."""

    pass


def dual_hash(data: bytes | str) -> str:
    """SHA256:BLAKE3 - ALWAYS use this, never single hash.

    Per CLAUDEME §8: Dual-hash every piece of data.
    """
    if isinstance(data, str):
        data = data.encode()
    sha = hashlib.sha256(data).hexdigest()
    b3 = blake3.blake3(data).hexdigest() if HAS_BLAKE3 else sha
    return f"{sha}:{b3}"


def emit_receipt(receipt_type: str, data: dict) -> dict:
    """Every function calls this. No exceptions.

    Per CLAUDEME LAW_1: No receipt → not real.
    """
    receipt = {
        "receipt_type": receipt_type,
        "ts": datetime.utcnow().isoformat() + "Z",
        "tenant_id": data.get("tenant_id", TENANT_ID),
        "payload_hash": dual_hash(json.dumps(data, sort_keys=True)),
        **data,
    }
    # Append to ledger (stdout in dev, file in prod)
    print(json.dumps(receipt), flush=True)
    return receipt


def merkle(items: list) -> str:
    """Compute Merkle root of items using dual_hash.

    Handles empty lists and odd counts per CLAUDEME spec.
    """
    if not items:
        return dual_hash(b"empty")
    hashes = [dual_hash(json.dumps(i, sort_keys=True)) for i in items]
    while len(hashes) > 1:
        if len(hashes) % 2:
            hashes.append(hashes[-1])
        hashes = [
            dual_hash(hashes[i] + hashes[i + 1]) for i in range(0, len(hashes), 2)
        ]
    return hashes[0]


# === STOPRULES ===


def stoprule_hash_mismatch(expected: str, actual: str) -> None:
    """Emit anomaly and halt on hash mismatch."""
    emit_receipt(
        "anomaly",
        {
            "metric": "hash_mismatch",
            "expected": expected,
            "actual": actual,
            "delta": -1,
            "action": "halt",
            "tenant_id": TENANT_ID,
        },
    )
    raise StopRule(f"Hash mismatch: expected {expected[:16]}..., got {actual[:16]}...")


def stoprule_unverified_claim(claim: dict) -> None:
    """Emit anomaly and escalate on unverified claim."""
    emit_receipt(
        "anomaly",
        {
            "metric": "unverified_claim",
            "claim": claim,
            "delta": -1,
            "action": "escalate",
            "tenant_id": TENANT_ID,
        },
    )
    raise StopRule(f"Unverified claim: {claim.get('type', 'unknown')}")


def emit_anomaly(
    metric: str, baseline: float, delta: float, classification: str, action: str
) -> dict:
    """Emit anomaly receipt - used by all stoprules.

    Classifications: drift, degradation, violation, deviation, anti_pattern
    Actions: alert, escalate, halt, auto_fix
    """
    return emit_receipt(
        "anomaly",
        {
            "metric": metric,
            "baseline": baseline,
            "delta": delta,
            "classification": classification,
            "action": action,
            "tenant_id": TENANT_ID,
        },
    )
