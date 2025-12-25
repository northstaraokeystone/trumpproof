"""GulfProof FARA Module

Foreign Agents Registration Act compliance tracking.

Key Data:
- Kushner: No FARA registration despite eight-figure foreign government payments
- Acting as "shadow diplomat" (Gaza ceasefire, Putin meetings, Trump campaign advisor)
- Wyden/Raskin requested special counsel investigation Oct 2024

Receipts: fara_assessment_receipt, fara_check_receipt, fara_violation_receipt
"""

from ..core import emit_receipt, TENANT_ID, emit_anomaly


def assess_fara_requirement(entity: dict, foreign_payments: list) -> dict:
    """Assess FARA registration requirement. Emit fara_assessment_receipt.

    FARA requires registration when:
    - Acting as agent of foreign principal
    - Engaged in political activities
    - Acting in public relations capacity
    - Soliciting/collecting money for foreign principal

    Args:
        entity: Entity to assess
        foreign_payments: List of payments from foreign sources

    Returns:
        fara_assessment_receipt
    """
    total_foreign_payments = sum(p.get("amount", 0) for p in foreign_payments)
    government_payments = [p for p in foreign_payments if p.get("is_government", False)]
    government_total = sum(p.get("amount", 0) for p in government_payments)

    # FARA triggers
    triggers = []

    if government_total > 0:
        triggers.append("received_government_payments")

    if entity.get("political_activities"):
        triggers.append("political_activities")

    if entity.get("public_relations"):
        triggers.append("public_relations_capacity")

    if entity.get("diplomatic_activities"):
        triggers.append("diplomatic_activities")

    requires_registration = len(triggers) >= 2 or government_total > 100_000

    return emit_receipt(
        "fara_assessment",
        {
            "tenant_id": TENANT_ID,
            "entity_id": entity.get("id", "unknown"),
            "entity_name": entity.get("name", "unknown"),
            "total_foreign_payments": total_foreign_payments,
            "government_payments": government_total,
            "payment_sources": [p.get("source", "unknown") for p in foreign_payments],
            "triggers": triggers,
            "requires_registration": requires_registration,
            "eight_figure_threshold": government_total >= 10_000_000,
        },
    )


def check_registration(
    entity_id: str, registered: bool = False, registration_date: str = None
) -> dict:
    """Check if entity is FARA registered. Emit fara_check_receipt.

    Args:
        entity_id: Entity identifier
        registered: Whether entity is registered
        registration_date: Date of registration if applicable

    Returns:
        fara_check_receipt
    """
    return emit_receipt(
        "fara_check",
        {
            "tenant_id": TENANT_ID,
            "entity_id": entity_id,
            "is_registered": registered,
            "registration_date": registration_date,
            "database_checked": "DOJ FARA Database",
            "check_timestamp": True,  # Will be added by emit_receipt
        },
    )


def flag_violation(entity_id: str, evidence: dict) -> dict:
    """Flag potential FARA violation. Emit fara_violation_receipt.

    Args:
        entity_id: Entity identifier
        evidence: Evidence of potential violation

    Returns:
        fara_violation_receipt
    """
    # Emit anomaly for tracking
    emit_anomaly(
        metric="fara_violation",
        baseline=0,
        delta=1,
        classification="violation",
        action="escalate",
    )

    severity = (
        "critical"
        if evidence.get("government_payments", 0) > 10_000_000
        else "high"
        if evidence.get("government_payments", 0) > 1_000_000
        else "medium"
    )

    return emit_receipt(
        "fara_violation",
        {
            "tenant_id": TENANT_ID,
            "entity_id": entity_id,
            "evidence": evidence,
            "foreign_payments": evidence.get("government_payments", 0),
            "registration_status": "unregistered",
            "activities": evidence.get("activities", []),
            "severity": severity,
            "special_counsel_requested": evidence.get(
                "special_counsel_requested", False
            ),
            "requesters": evidence.get("requesters", []),  # e.g., ["Wyden", "Raskin"]
        },
    )
