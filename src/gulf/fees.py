"""GulfProof Fees Module

Management fee transparency.

Key Metrics:
- $157M total management fees collected
- $87M from Saudi PIF
- Zero returns to investors
- Another $90M guaranteed through Aug 2026

Receipts: fee_receipt, ratio_receipt, excessive_fee_receipt
"""

from ..core import emit_receipt, TENANT_ID, emit_anomaly
from ..constants import FEE_TO_RETURNS_EXCESSIVE, GULF_FEES_COLLECTED


def track_fee(fund_id: str, fee: dict) -> dict:
    """Track management fee. Emit fee_receipt.

    Args:
        fund_id: Fund identifier
        fee: Fee details

    Returns:
        fee_receipt
    """
    return emit_receipt(
        "management_fee",
        {
            "tenant_id": TENANT_ID,
            "fund_id": fund_id,
            "fee_type": fee.get("type", "management"),
            "fee_amount": fee.get("amount", 0),
            "fee_period": fee.get("period", "unknown"),
            "source": fee.get("source", "unknown"),
            "is_guaranteed": fee.get("guaranteed", False),
            "aum_at_time": fee.get("aum", 0),
            "fee_percentage": (
                fee.get("amount", 0) / fee.get("aum", 1) * 100
                if fee.get("aum", 0) > 0
                else 0
            ),
        },
    )


def compute_fee_ratio(fees: float, returns: float) -> dict:
    """Compute fee-to-returns ratio. Emit ratio_receipt.

    Handles edge case of zero returns (returns infinity).

    Args:
        fees: Total fees collected
        returns: Total returns generated

    Returns:
        ratio_receipt
    """
    if returns == 0:
        # Zero returns case - fees collected on nothing
        ratio = float("inf")
        ratio_classification = "infinite"
    elif returns < 0:
        # Negative returns - even worse
        ratio = abs(fees / returns)
        ratio_classification = "negative_returns"
    else:
        ratio = fees / returns
        ratio_classification = "calculated"

    excessive = ratio > FEE_TO_RETURNS_EXCESSIVE or ratio == float("inf")

    return emit_receipt(
        "fee_ratio",
        {
            "tenant_id": TENANT_ID,
            "fees_collected": fees,
            "returns_generated": returns,
            "ratio": ratio if ratio != float("inf") else "infinity",
            "ratio_classification": ratio_classification,
            "threshold": FEE_TO_RETURNS_EXCESSIVE,
            "excessive": excessive,
            "affinity_baseline_fees": GULF_FEES_COLLECTED,
            "affinity_baseline_returns": 0,  # Zero returns documented
        },
    )


def flag_excessive(ratio: float, threshold: float = FEE_TO_RETURNS_EXCESSIVE) -> dict:
    """Flag excessive fees. Emit excessive_fee_receipt.

    Args:
        ratio: Fee-to-returns ratio
        threshold: Threshold for excessive classification

    Returns:
        excessive_fee_receipt
    """
    is_excessive = ratio > threshold or ratio == float("inf")

    if is_excessive:
        emit_anomaly(
            metric="excessive_fees",
            baseline=threshold,
            delta=ratio - threshold if ratio != float("inf") else 100,
            classification="deviation",
            action="alert",
        )

    severity = (
        "critical"
        if ratio == float("inf") or ratio > threshold * 10
        else "high"
        if ratio > threshold * 5
        else "medium"
        if ratio > threshold
        else "low"
    )

    return emit_receipt(
        "excessive_fee_flag",
        {
            "tenant_id": TENANT_ID,
            "ratio": ratio if ratio != float("inf") else "infinity",
            "threshold": threshold,
            "is_excessive": is_excessive,
            "severity": severity,
            "recommendation": "review_fee_structure" if is_excessive else "none",
        },
    )
