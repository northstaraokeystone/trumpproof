"""TariffProof Exemption Module

Exemption application and approval tracking.
Detect opacity and favoritism patterns.
Receipts: exemption_application_receipt, exemption_outcome_receipt,
          favoritism_detection_receipt, opacity_receipt

Key Metrics (from ProPublica research):
- First-term exemptions functioned as "spoils system"
- Politically connected firms significantly more likely to receive exemptions
- Current process: no applications, no criteria, arbitrary inclusions
"""

from ..core import emit_receipt, dual_hash, TENANT_ID
from ..constants import FAVORITISM_THRESHOLD, OPACITY_CRITICAL


def register_exemption(application: dict) -> dict:
    """Register exemption request. Emit exemption_application_receipt.

    Args:
        application: Exemption application details

    Returns:
        exemption_application_receipt
    """
    return emit_receipt("exemption_application", {
        "tenant_id": TENANT_ID,
        "applicant": application.get("applicant", "unknown"),
        "product": application.get("product", "unknown"),
        "hts_code": application.get("hts_code", ""),
        "amount_requested": application.get("amount_requested", 0),
        "justification": application.get("justification", ""),
        "application_hash": dual_hash(str(application)),
    })


def track_approval(exemption_id: str, outcome: str, rationale: str,
                   lobbying_cross_ref: str = "") -> dict:
    """Track approval/denial with rationale. Emit exemption_outcome_receipt.

    Args:
        exemption_id: ID of the exemption application
        outcome: "approved" or "denied"
        rationale: Explanation for decision
        lobbying_cross_ref: Reference to any lobbying disclosures

    Returns:
        exemption_outcome_receipt
    """
    return emit_receipt("exemption_outcome", {
        "tenant_id": TENANT_ID,
        "exemption_id": exemption_id,
        "outcome": outcome,
        "rationale": rationale,
        "lobbying_cross_ref": lobbying_cross_ref,
        "has_documented_criteria": bool(rationale and len(rationale) > 10),
    })


def detect_favoritism(outcomes: list, lobbying_data: list) -> dict:
    """Cross-reference outcomes with lobbying. Emit favoritism_detection_receipt.

    Args:
        outcomes: List of exemption outcomes
        lobbying_data: List of lobbying disclosures

    Returns:
        favoritism_detection_receipt with correlation analysis
    """
    # Build lobbying lookup
    lobbyist_entities = set()
    for filing in lobbying_data:
        client = filing.get("client", "")
        if client:
            lobbyist_entities.add(client.lower())

    # Analyze outcomes
    total = len(outcomes)
    approved = 0
    approved_with_lobbying = 0
    approved_without_lobbying = 0
    denied_with_lobbying = 0
    denied_without_lobbying = 0

    for outcome in outcomes:
        applicant = outcome.get("applicant", "").lower()
        is_approved = outcome.get("outcome") == "approved"
        has_lobbyist = applicant in lobbyist_entities

        if is_approved:
            approved += 1
            if has_lobbyist:
                approved_with_lobbying += 1
            else:
                approved_without_lobbying += 1
        else:
            if has_lobbyist:
                denied_with_lobbying += 1
            else:
                denied_without_lobbying += 1

    # Calculate rates
    lobbying_total = approved_with_lobbying + denied_with_lobbying
    non_lobbying_total = approved_without_lobbying + denied_without_lobbying

    lobbying_approval_rate = (
        approved_with_lobbying / lobbying_total if lobbying_total > 0 else 0
    )
    baseline_approval_rate = (
        approved_without_lobbying / non_lobbying_total if non_lobbying_total > 0 else 0
    )

    deviation = abs(lobbying_approval_rate - baseline_approval_rate)
    favoritism_detected = deviation > FAVORITISM_THRESHOLD

    return emit_receipt("favoritism_detection", {
        "tenant_id": TENANT_ID,
        "total_outcomes": total,
        "approved_count": approved,
        "lobbying_approval_rate": lobbying_approval_rate,
        "baseline_approval_rate": baseline_approval_rate,
        "deviation_score": deviation,
        "threshold": FAVORITISM_THRESHOLD,
        "favoritism_detected": favoritism_detected,
        "connected_entities": list(lobbyist_entities),
    })


def score_opacity(exemptions: list) -> dict:
    """Compute opacity score (0-1). Emit opacity_receipt.

    Opacity factors:
    - Missing rationale
    - Missing criteria documentation
    - No public notice
    - Arbitrary timing

    Args:
        exemptions: List of exemption records

    Returns:
        opacity_receipt with score
    """
    if not exemptions:
        return emit_receipt("opacity", {
            "tenant_id": TENANT_ID,
            "opacity_score": 1.0,
            "classification": "critical",
            "message": "No exemption data available - maximum opacity",
        })

    opacity_factors = 0
    total_factors = 0

    for ex in exemptions:
        # Check each opacity factor
        total_factors += 4

        # Missing rationale
        if not ex.get("rationale"):
            opacity_factors += 1

        # Missing criteria
        if not ex.get("criteria"):
            opacity_factors += 1

        # No public notice
        if not ex.get("public_notice"):
            opacity_factors += 1

        # Arbitrary timing (decided same day or no date)
        if ex.get("same_day_decision") or not ex.get("decision_date"):
            opacity_factors += 1

    opacity_score = opacity_factors / total_factors if total_factors > 0 else 1.0

    classification = "critical" if opacity_score >= OPACITY_CRITICAL else \
                     "high" if opacity_score >= 0.6 else \
                     "medium" if opacity_score >= 0.4 else "low"

    return emit_receipt("opacity", {
        "tenant_id": TENANT_ID,
        "exemptions_analyzed": len(exemptions),
        "opacity_factors": opacity_factors,
        "total_factors": total_factors,
        "opacity_score": opacity_score,
        "threshold_critical": OPACITY_CRITICAL,
        "classification": classification,
    })
