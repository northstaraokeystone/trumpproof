"""BorderProof Citizenship Module

Citizenship verification BEFORE deportation.

Key Cases (from ProPublica):
- Disabled military veteran detained
- 2-year-old citizen deported to Honduras
- 170+ U.S. citizens wrongfully detained in first 9 months

Receipts: citizenship_verification_receipt, citizen_flag_receipt, wrongful_detention_receipt
"""

from ..core import emit_receipt, TENANT_ID, emit_anomaly


def verify_citizenship(detainee_id: str, documents: list) -> dict:
    """Verify citizenship status. Emit citizenship_verification_receipt.

    Args:
        detainee_id: Anonymized detainee ID
        documents: List of documents reviewed

    Returns:
        citizenship_verification_receipt
    """
    document_types = [d.get("type", "unknown") for d in documents]

    # Score document strength
    strong_docs = ["passport", "birth_certificate", "naturalization_certificate"]
    medium_docs = ["ssn_card", "drivers_license", "military_id"]

    strong_count = sum(1 for d in document_types if d.lower() in strong_docs)
    medium_count = sum(1 for d in document_types if d.lower() in medium_docs)

    if strong_count > 0:
        verification_strength = "high"
        citizenship_likely = any(d.get("indicates_citizenship", False) for d in documents)
    elif medium_count > 0:
        verification_strength = "medium"
        citizenship_likely = any(d.get("indicates_citizenship", False) for d in documents)
    else:
        verification_strength = "low"
        citizenship_likely = False

    return emit_receipt("citizenship_verification", {
        "tenant_id": TENANT_ID,
        "detainee_id": detainee_id,
        "documents_reviewed": len(documents),
        "document_types": document_types,
        "strong_document_count": strong_count,
        "medium_document_count": medium_count,
        "verification_strength": verification_strength,
        "citizenship_likely": citizenship_likely,
        "requires_further_review": verification_strength == "low" or citizenship_likely,
    })


def flag_us_citizen(detainee_id: str, evidence: dict) -> dict:
    """Flag potential U.S. citizen. Emit citizen_flag_receipt.

    This is a CRITICAL function - wrongful deportation of citizens is unconstitutional.

    Args:
        detainee_id: Anonymized detainee ID
        evidence: Evidence of citizenship

    Returns:
        citizen_flag_receipt
    """
    # Emit anomaly for tracking
    emit_anomaly(
        metric="potential_citizen_detention",
        baseline=0,
        delta=1,
        classification="violation",
        action="escalate"
    )

    return emit_receipt("citizen_flag", {
        "tenant_id": TENANT_ID,
        "detainee_id": detainee_id,
        "evidence_type": evidence.get("type", "unknown"),
        "evidence_description": evidence.get("description", ""),
        "evidence_strength": evidence.get("strength", "unknown"),
        "birthplace": evidence.get("birthplace", "unknown"),
        "parent_citizenship": evidence.get("parent_citizenship", "unknown"),
        "military_service": evidence.get("military_service", False),
        "priority": "CRITICAL",
        "action_required": "IMMEDIATE_REVIEW",
    })


def track_wrongful_detention(cases: list) -> dict:
    """Track wrongful detention cases. Emit wrongful_detention_receipt.

    Args:
        cases: List of wrongful detention cases

    Returns:
        wrongful_detention_receipt with aggregate statistics
    """
    total_cases = len(cases)
    total_days = sum(c.get("detention_days", 0) for c in cases)

    # Categorize cases
    categories = {
        "military_veteran": 0,
        "minor": 0,
        "disabled": 0,
        "elderly": 0,
        "other": 0,
    }

    for case in cases:
        if case.get("military_veteran"):
            categories["military_veteran"] += 1
        if case.get("age", 99) < 18:
            categories["minor"] += 1
        if case.get("disabled"):
            categories["disabled"] += 1
        if case.get("age", 0) >= 65:
            categories["elderly"] += 1
        if not any([case.get("military_veteran"), case.get("age", 99) < 18,
                    case.get("disabled"), case.get("age", 0) >= 65]):
            categories["other"] += 1

    # Resolution tracking
    resolved = sum(1 for c in cases if c.get("resolved"))
    still_detained = sum(1 for c in cases if not c.get("resolved") and not c.get("deported"))
    wrongfully_deported = sum(1 for c in cases if c.get("deported"))

    return emit_receipt("wrongful_detention_tracking", {
        "tenant_id": TENANT_ID,
        "total_cases": total_cases,
        "total_wrongful_detention_days": total_days,
        "average_detention_days": total_days / total_cases if total_cases > 0 else 0,
        "categories": categories,
        "resolved": resolved,
        "still_detained": still_detained,
        "wrongfully_deported": wrongfully_deported,
        "documented_baseline": 170,  # ProPublica: 170+ in first 9 months
        "constitutional_violations": total_cases,  # Each is a potential 4th/5th/14th Amendment violation
    })
