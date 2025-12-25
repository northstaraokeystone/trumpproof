"""Loop Harvest Module

Gap collection from violations and manual interventions.

Receipts: harvest_receipt, proposal_receipt
"""

from ..core import emit_receipt, TENANT_ID
from ..constants import HARVEST_PERIOD_DAYS


def harvest_violations(receipts: list, period: str = None) -> dict:
    """Collect violations from all modules. Emit harvest_receipt.

    Args:
        receipts: List of all receipts
        period: Reporting period (default: last HARVEST_PERIOD_DAYS days)

    Returns:
        harvest_receipt with violations
    """
    period = period or f"last_{HARVEST_PERIOD_DAYS}_days"

    violations = []
    for r in receipts:
        # Identify violations
        if r.get("receipt_type") == "anomaly":
            violations.append(r)
        elif r.get("violation") or r.get("is_violation"):
            violations.append(r)
        elif r.get("exceeds_threshold") or r.get("excessive"):
            violations.append(r)
        elif r.get("favoritism_detected"):
            violations.append(r)
        elif r.get("is_emolument"):
            violations.append(r)
        elif r.get("fara_violation"):
            violations.append(r)

    # Group by module
    by_module = {}
    for v in violations:
        module = infer_module_from_receipt(v)
        if module not in by_module:
            by_module[module] = []
        by_module[module].append(v)

    return emit_receipt("harvest", {
        "tenant_id": TENANT_ID,
        "period": period,
        "total_violations": len(violations),
        "by_module": {k: len(v) for k, v in by_module.items()},
        "violations": violations,
        "harvest_period_days": HARVEST_PERIOD_DAYS,
    })


def infer_module_from_receipt(receipt: dict) -> str:
    """Infer module from receipt content."""
    receipt_type = receipt.get("receipt_type", "").lower()

    if "tariff" in receipt_type or "exemption" in receipt_type:
        return "tariff"
    elif "detention" in receipt_type or "border" in receipt_type:
        return "border"
    elif "swf" in receipt_type or "fara" in receipt_type or "fee" in receipt_type:
        return "gulf"
    elif "golf" in receipt_type or "liv" in receipt_type or "emolument" in receipt_type:
        return "golf"
    elif "license" in receipt_type or "ownership" in receipt_type:
        return "license"
    else:
        return "unknown"


def rank_by_exposure(violations: list) -> list:
    """Rank by dollar exposure. Return ranked list.

    Args:
        violations: List of violation records

    Returns:
        List sorted by exposure (highest first)
    """
    def get_exposure(v):
        # Try various exposure fields
        return (
            v.get("amount", 0) or
            v.get("total_amount", 0) or
            v.get("exposure", 0) or
            v.get("liability", 0) or
            v.get("fees_collected", 0) or
            0
        )

    ranked = sorted(violations, key=get_exposure, reverse=True)
    return ranked


def propose_remediation(violations: list) -> dict:
    """Propose remediation for recurring patterns. Emit proposal_receipt.

    Args:
        violations: List of violations to analyze

    Returns:
        proposal_receipt with remediation proposals
    """
    proposals = []

    # Count by type
    by_type = {}
    for v in violations:
        vtype = v.get("receipt_type", "unknown")
        if vtype not in by_type:
            by_type[vtype] = 0
        by_type[vtype] += 1

    # Propose remediation for recurring patterns
    for vtype, count in by_type.items():
        if count >= 3:  # Recurring pattern
            proposals.append({
                "violation_type": vtype,
                "occurrence_count": count,
                "proposed_action": get_remediation_action(vtype),
                "priority": "high" if count >= 5 else "medium",
            })

    return emit_receipt("remediation_proposal", {
        "tenant_id": TENANT_ID,
        "violations_analyzed": len(violations),
        "recurring_patterns": len(proposals),
        "proposals": proposals,
    })


def get_remediation_action(violation_type: str) -> str:
    """Get proposed remediation action for violation type."""
    remediation_map = {
        "favoritism_detection": "implement_blind_review_process",
        "excessive_fee": "fee_structure_review",
        "fara_violation": "doj_referral",
        "emolument": "disclosure_requirement",
        "citizen_flag": "immediate_review_protocol",
        "death_rate": "facility_inspection_mandate",
        "opacity": "beneficial_ownership_disclosure",
    }

    for key, action in remediation_map.items():
        if key in violation_type.lower():
            return action

    return "manual_review_required"
