"""TariffProof Revenue Module

Track tariff revenue collection and allocation.
Receipts: tariff_ingest_receipt, allocation_receipt, verification_receipt, trend_receipt
SLOs: Ingest ≤50ms p95, Verification ≤100ms p95
"""

from ..core import emit_receipt, dual_hash, TENANT_ID
from ..constants import TARIFF_FY2025_REVENUE


def ingest_customs_data(data: dict, tenant_id: str = TENANT_ID) -> dict:
    """Ingest CBP revenue data. Emit tariff_ingest_receipt.

    Args:
        data: CBP customs revenue data
        tenant_id: Tenant identifier

    Returns:
        tariff_ingest_receipt with payload hash
    """
    return emit_receipt(
        "tariff_ingest",
        {
            "tenant_id": tenant_id,
            "revenue_amount": data.get("revenue_amount", 0),
            "period": data.get("period", "unknown"),
            "source": data.get("source", "cbp"),
            "data_hash": dual_hash(str(data)),
        },
    )


def compute_allocation(revenue: float, categories: list) -> dict:
    """Allocate revenue by category. Emit allocation_receipt.

    Args:
        revenue: Total revenue amount
        categories: List of allocation categories with percentages

    Returns:
        allocation_receipt with breakdown
    """
    allocations = {}
    for cat in categories:
        name = cat.get("name", "unknown")
        pct = cat.get("percentage", 0)
        allocations[name] = revenue * (pct / 100)

    return emit_receipt(
        "tariff_allocation",
        {
            "tenant_id": TENANT_ID,
            "total_revenue": revenue,
            "categories": categories,
            "allocations": allocations,
            "fy2025_baseline": TARIFF_FY2025_REVENUE,
        },
    )


def verify_claimed_vs_actual(claimed: dict, actual: dict) -> dict:
    """Compare claimed vs CBP data. Emit verification_receipt.

    Args:
        claimed: Claimed revenue figures
        actual: Actual CBP revenue data

    Returns:
        verification_receipt with discrepancies
    """
    discrepancies = {}
    for key in claimed:
        if key in actual:
            diff = claimed[key] - actual[key]
            if abs(diff) > 0.01:  # Tolerance
                discrepancies[key] = {
                    "claimed": claimed[key],
                    "actual": actual[key],
                    "difference": diff,
                    "percentage_diff": (diff / actual[key] * 100) if actual[key] else 0,
                }

    match_status = "verified" if not discrepancies else "discrepancy_detected"

    return emit_receipt(
        "tariff_verification",
        {
            "tenant_id": TENANT_ID,
            "claimed": claimed,
            "actual": actual,
            "discrepancies": discrepancies,
            "match_status": match_status,
            "discrepancy_count": len(discrepancies),
        },
    )


def track_trend(receipts: list, window: int = 12) -> dict:
    """Compute revenue trend over window. Emit trend_receipt.

    Args:
        receipts: List of previous tariff receipts
        window: Number of periods to analyze

    Returns:
        trend_receipt with trend analysis
    """
    values = []
    for r in receipts[-window:]:
        if "revenue_amount" in r:
            values.append(r["revenue_amount"])

    if len(values) < 2:
        trend = "insufficient_data"
        slope = 0
    else:
        # Simple linear trend
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * v for i, v in enumerate(values))
        x2_sum = sum(i * i for i in range(n))

        denominator = n * x2_sum - x_sum * x_sum
        if denominator != 0:
            slope = (n * xy_sum - x_sum * y_sum) / denominator
            trend = "increasing" if slope > 0 else "decreasing" if slope < 0 else "flat"
        else:
            slope = 0
            trend = "flat"

    return emit_receipt(
        "tariff_trend",
        {
            "tenant_id": TENANT_ID,
            "window": window,
            "data_points": len(values),
            "trend": trend,
            "slope": slope,
            "latest_value": values[-1] if values else 0,
            "fy2025_target": TARIFF_FY2025_REVENUE,
        },
    )
