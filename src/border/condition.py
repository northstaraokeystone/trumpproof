"""BorderProof Condition Module

Detention condition monitoring.

Key Data:
- 2025 deadliest year for ICE custody since 2004
- 30-32 deaths documented (including 4 deaths in 4 days Dec 12-15)
- Fort Bliss violated 60+ federal detention standards in first 50 days
- Class-action lawsuit: California City facility described as "torture chamber"

Receipts: condition_receipt, violation_receipt, death_rate_receipt
"""

from ..core import emit_receipt, TENANT_ID, emit_anomaly


def assess_conditions(facility_id: str, inspection: dict) -> dict:
    """Assess conditions against standards. Emit condition_receipt.

    Args:
        facility_id: Facility identifier
        inspection: Inspection results

    Returns:
        condition_receipt
    """
    standards = {
        "medical_care": inspection.get("medical_care_adequate", False),
        "food_quality": inspection.get("food_quality_adequate", False),
        "sanitation": inspection.get("sanitation_adequate", False),
        "recreation": inspection.get("recreation_access", False),
        "communication": inspection.get("communication_access", False),
        "legal_access": inspection.get("legal_access", False),
        "sleeping_conditions": inspection.get("sleeping_conditions_adequate", False),
        "climate_control": inspection.get("climate_control_adequate", False),
    }

    met_count = sum(1 for v in standards.values() if v)
    total_count = len(standards)
    compliance_rate = met_count / total_count if total_count > 0 else 0

    classification = "adequate" if compliance_rate >= 0.9 else \
                     "deficient" if compliance_rate >= 0.7 else \
                     "critical" if compliance_rate >= 0.5 else "dangerous"

    return emit_receipt("condition_assessment", {
        "tenant_id": TENANT_ID,
        "facility_id": facility_id,
        "inspection_date": inspection.get("date", "unknown"),
        "standards_assessed": standards,
        "standards_met": met_count,
        "standards_total": total_count,
        "compliance_rate": compliance_rate,
        "classification": classification,
        "inspector": inspection.get("inspector", "unknown"),
        "notes": inspection.get("notes", ""),
    })


def track_violations(facility_id: str, violations: list) -> dict:
    """Track standards violations. Emit violation_receipt.

    Args:
        facility_id: Facility identifier
        violations: List of violation records

    Returns:
        violation_receipt
    """
    # Categorize violations
    categories = {
        "medical": 0,
        "safety": 0,
        "sanitation": 0,
        "overcrowding": 0,
        "staff_conduct": 0,
        "legal_access": 0,
        "other": 0,
    }

    critical_count = 0
    for v in violations:
        cat = v.get("category", "other").lower()
        if cat in categories:
            categories[cat] += 1
        else:
            categories["other"] += 1

        if v.get("severity") == "critical":
            critical_count += 1

    # Emit anomaly if critical violations
    if critical_count > 0:
        emit_anomaly(
            metric="critical_violations",
            baseline=0,
            delta=critical_count,
            classification="violation",
            action="escalate"
        )

    return emit_receipt("violation_tracking", {
        "tenant_id": TENANT_ID,
        "facility_id": facility_id,
        "total_violations": len(violations),
        "critical_violations": critical_count,
        "violations_by_category": categories,
        "violations": violations,
        "fort_bliss_baseline": 60,  # Fort Bliss violated 60+ standards in 50 days
        "exceeds_baseline": len(violations) > 60,
    })


def compute_death_rate(facility_id: str, period: str,
                       deaths: int = 0, detainee_days: int = 0) -> dict:
    """Compute death rate per 10K detainee-days. Emit death_rate_receipt.

    Args:
        facility_id: Facility identifier
        period: Reporting period
        deaths: Number of deaths
        detainee_days: Total detainee-days in period

    Returns:
        death_rate_receipt
    """
    rate_per_10k = (deaths / detainee_days * 10000) if detainee_days > 0 else 0

    # Historical baseline: pre-2025 average
    BASELINE_RATE = 0.5  # deaths per 10K detainee-days (approximate)

    # Emit anomaly if rate exceeds baseline
    if rate_per_10k > BASELINE_RATE * 2:
        emit_anomaly(
            metric="death_rate",
            baseline=BASELINE_RATE,
            delta=rate_per_10k - BASELINE_RATE,
            classification="degradation",
            action="halt"
        )

    return emit_receipt("death_rate", {
        "tenant_id": TENANT_ID,
        "facility_id": facility_id,
        "period": period,
        "deaths": deaths,
        "detainee_days": detainee_days,
        "rate_per_10k_days": rate_per_10k,
        "baseline_rate": BASELINE_RATE,
        "exceeds_baseline": rate_per_10k > BASELINE_RATE,
        "rate_multiplier": rate_per_10k / BASELINE_RATE if BASELINE_RATE > 0 else 0,
        "fy2025_deaths_documented": 32,  # 30-32 deaths documented
        "deadliest_since": 2004,
    })
