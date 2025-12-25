"""BorderProof Detention Module

Per-detainee tracking and facility monitoring.
Receipts: detention_receipt, duration_receipt, facility_receipt, cost_receipt
SLOs: Facility metrics ≤24h staleness, Cost computation ≤1s p95
"""

from datetime import datetime
from ..core import emit_receipt, dual_hash, TENANT_ID
from ..constants import BORDER_ICE_FY2025


def register_detainee(detainee: dict, facility_id: str) -> dict:
    """Register detainee with anonymized ID. Emit detention_receipt.

    Privacy note: Uses anonymized tracking only, no PII stored.

    Args:
        detainee: Detainee data (anonymized)
        facility_id: Facility identifier

    Returns:
        detention_receipt
    """
    # Generate anonymized ID from data hash
    anonymized_id = dual_hash(str(detainee))[:16]

    return emit_receipt(
        "detention",
        {
            "tenant_id": TENANT_ID,
            "anonymized_id": anonymized_id,
            "facility_id": facility_id,
            "intake_date": detainee.get("intake_date", datetime.utcnow().isoformat()),
            "category": detainee.get("category", "unknown"),
            "citizenship_verified": detainee.get("citizenship_verified", False),
        },
    )


def track_duration(
    detainee_id: str, intake_date: str = None, current_date: str = None
) -> dict:
    """Track detention duration. Emit duration_receipt.

    Args:
        detainee_id: Anonymized detainee ID
        intake_date: Date of intake (ISO format)
        current_date: Current date for calculation (defaults to now)

    Returns:
        duration_receipt
    """
    if intake_date:
        intake = datetime.fromisoformat(intake_date.replace("Z", "+00:00"))
    else:
        intake = datetime.utcnow()

    if current_date:
        current = datetime.fromisoformat(current_date.replace("Z", "+00:00"))
    else:
        current = datetime.utcnow()

    duration_days = (current - intake).days

    return emit_receipt(
        "detention_duration",
        {
            "tenant_id": TENANT_ID,
            "detainee_id": detainee_id,
            "intake_date": intake.isoformat(),
            "current_date": current.isoformat(),
            "duration_days": duration_days,
            "extended_detention": duration_days > 90,  # Flag extended
        },
    )


def monitor_facility(facility_id: str, metrics: dict) -> dict:
    """Monitor facility conditions. Emit facility_receipt.

    Args:
        facility_id: Facility identifier
        metrics: Current facility metrics

    Returns:
        facility_receipt
    """
    capacity = metrics.get("capacity", 0)
    current_population = metrics.get("current_population", 0)
    occupancy_rate = current_population / capacity if capacity > 0 else 0

    return emit_receipt(
        "facility_monitor",
        {
            "tenant_id": TENANT_ID,
            "facility_id": facility_id,
            "capacity": capacity,
            "current_population": current_population,
            "occupancy_rate": occupancy_rate,
            "overcrowded": occupancy_rate > 1.0,
            "staffing_ratio": metrics.get("staffing_ratio", 0),
            "medical_staff_available": metrics.get("medical_staff_available", False),
            "last_inspection_date": metrics.get("last_inspection_date", "unknown"),
            "violations_count": metrics.get("violations_count", 0),
        },
    )


def compute_cost_per_detainee(
    facility_id: str,
    period: str,
    total_cost: float = None,
    population: int = None,
    days: int = None,
) -> dict:
    """Compute cost per detainee per day. Emit cost_receipt.

    Key comparison:
    - Standard facility: ~$150/day
    - Guantanamo transfers: $100K+/day

    Args:
        facility_id: Facility identifier
        period: Reporting period
        total_cost: Total facility cost for period
        population: Average population
        days: Days in period

    Returns:
        cost_receipt
    """
    if total_cost and population and days:
        detainee_days = population * days
        cost_per_day = total_cost / detainee_days if detainee_days > 0 else 0
    else:
        cost_per_day = 0
        detainee_days = 0

    # Flag excessive cost
    STANDARD_COST = 150  # $150/day baseline
    cost_multiplier = cost_per_day / STANDARD_COST if STANDARD_COST > 0 else 0
    excessive = cost_multiplier > 10  # 10x standard = excessive

    return emit_receipt(
        "detention_cost",
        {
            "tenant_id": TENANT_ID,
            "facility_id": facility_id,
            "period": period,
            "total_cost": total_cost or 0,
            "average_population": population or 0,
            "detainee_days": detainee_days,
            "cost_per_detainee_day": cost_per_day,
            "standard_baseline": STANDARD_COST,
            "cost_multiplier": cost_multiplier,
            "excessive_cost_flag": excessive,
            "ice_fy2025_budget": BORDER_ICE_FY2025,
        },
    )
