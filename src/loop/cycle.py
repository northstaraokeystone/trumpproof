"""Loop Cycle Module

60-second SENSE→ACTUATE cycle per ProofPack v3 specification.

Receipts: loop_cycle_receipt
"""

import time
from ..core import emit_receipt, TENANT_ID, dual_hash
from ..constants import LOOP_CYCLE_SECONDS, MODULE_PRIORITY


def run_cycle(receipts: list = None, cycle_id: str = None) -> dict:
    """Execute full SENSE→EMIT cycle. Emit loop_cycle_receipt. Return metrics.

    Args:
        receipts: Current receipt stream from all modules
        cycle_id: Optional cycle identifier

    Returns:
        loop_cycle_receipt with cycle metrics
    """
    receipts = receipts or []
    cycle_id = cycle_id or dual_hash(str(time.time()))[:16]

    start_time = time.time()

    # SENSE: Query receipt stream
    state = sense(receipts)

    # ANALYZE: Run cross-domain pattern detection
    analysis = analyze(state)

    # Compute cycle time
    cycle_time_ms = (time.time() - start_time) * 1000

    return emit_cycle_receipt(
        cycle_id,
        {
            "receipts_processed": len(receipts),
            "state": state,
            "analysis": analysis,
            "cycle_time_ms": cycle_time_ms,
            "target_cycle_seconds": LOOP_CYCLE_SECONDS,
        },
    )


def sense(receipts: list) -> dict:
    """Query receipt stream from all modules. Return aggregated state.

    Args:
        receipts: List of receipts from all modules

    Returns:
        Aggregated state dictionary
    """
    state = {
        "by_module": {},
        "by_type": {},
        "anomalies": [],
        "total_receipts": len(receipts),
    }

    for r in receipts:
        # Group by module (inferred from receipt type)
        receipt_type = r.get("receipt_type", "unknown")
        module = infer_module(receipt_type)

        if module not in state["by_module"]:
            state["by_module"][module] = {"count": 0, "receipts": []}
        state["by_module"][module]["count"] += 1
        state["by_module"][module]["receipts"].append(r)

        # Group by receipt type
        if receipt_type not in state["by_type"]:
            state["by_type"][receipt_type] = 0
        state["by_type"][receipt_type] += 1

        # Collect anomalies
        if receipt_type == "anomaly":
            state["anomalies"].append(r)

    return state


def infer_module(receipt_type: str) -> str:
    """Infer module from receipt type."""
    type_lower = receipt_type.lower()

    if "tariff" in type_lower or "exemption" in type_lower or "refund" in type_lower:
        return "tariff"
    elif (
        "detention" in type_lower
        or "border" in type_lower
        or "citizenship" in type_lower
    ):
        return "border"
    elif "swf" in type_lower or "fara" in type_lower or "investment" in type_lower:
        return "gulf"
    elif "golf" in type_lower or "liv" in type_lower or "emolument" in type_lower:
        return "golf"
    elif (
        "license" in type_lower or "ownership" in type_lower or "partner" in type_lower
    ):
        return "license"
    elif "pif" in type_lower or "cross" in type_lower or "loop" in type_lower:
        return "loop"
    else:
        return "unknown"


def analyze(state: dict) -> dict:
    """Run cross-domain pattern detection. Return anomalies.

    Args:
        state: Aggregated state from sense()

    Returns:
        Analysis results
    """
    analysis = {
        "modules_active": list(state.get("by_module", {}).keys()),
        "anomaly_count": len(state.get("anomalies", [])),
        "cross_domain_patterns": [],
        "priority_violations": [],
    }

    # Check for priority module activity
    for module in MODULE_PRIORITY:
        if module in state.get("by_module", {}):
            module_data = state["by_module"][module]
            # Check for violations/anomalies in this module
            for r in module_data.get("receipts", []):
                if (
                    r.get("violation")
                    or r.get("exceeds_threshold")
                    or r.get("excessive")
                    or r.get("favoritism_detected")
                ):
                    analysis["priority_violations"].append(
                        {
                            "module": module,
                            "receipt_type": r.get("receipt_type"),
                            "details": r,
                        }
                    )

    return analysis


def emit_cycle_receipt(cycle_id: str, metrics: dict) -> dict:
    """Emit cycle completion receipt.

    Args:
        cycle_id: Cycle identifier
        metrics: Cycle metrics

    Returns:
        loop_cycle_receipt
    """
    return emit_receipt(
        "loop_cycle",
        {
            "tenant_id": TENANT_ID,
            "cycle_id": cycle_id,
            "receipts_processed": metrics.get("receipts_processed", 0),
            "modules_active": metrics.get("analysis", {}).get("modules_active", []),
            "anomalies_detected": metrics.get("analysis", {}).get("anomaly_count", 0),
            "priority_violations": len(
                metrics.get("analysis", {}).get("priority_violations", [])
            ),
            "cycle_time_ms": metrics.get("cycle_time_ms", 0),
            "target_cycle_seconds": metrics.get(
                "target_cycle_seconds", LOOP_CYCLE_SECONDS
            ),
            "within_target": metrics.get("cycle_time_ms", 0)
            < LOOP_CYCLE_SECONDS * 1000,
        },
    )
