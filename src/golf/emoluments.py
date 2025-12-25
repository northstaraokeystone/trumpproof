"""GolfProof Emoluments Module

Emoluments clause compliance tracking.

Legal Precedent:
- Judge Messitte ruling (2017): "emolument" means "almost anything of value" from foreign governments
- First-ever judicial interpretation of emoluments clause
- Precedent vacated when cases dismissed as moot Jan 2021

Key Data:
- $7.8M minimum documented from 20+ foreign governments (first term)
- Up to $160M total estimated

Receipts: emolument_assessment_receipt, government_tracking_receipt, exposure_receipt
"""

from ..core import emit_receipt, TENANT_ID, emit_anomaly
from ..constants import EMOLUMENTS_DISCLOSURE_THRESHOLD


def assess_emolument(payment: dict, source: dict) -> dict:
    """Assess if payment constitutes emolument. Emit emolument_assessment_receipt.

    Per Messitte ruling: "emolument" = almost anything of value from foreign governments

    Args:
        payment: Payment details
        source: Payment source details

    Returns:
        emolument_assessment_receipt
    """
    # Emolument criteria
    is_foreign = source.get("country", "").lower() not in ["us", "usa", "united states"]
    is_government = source.get("is_government", False) or \
                    source.get("is_state_owned", False) or \
                    source.get("is_sovereign", False)
    amount = payment.get("amount", 0)

    # Per Messitte: "almost anything of value"
    is_emolument = is_foreign and is_government and amount > 0

    if is_emolument and amount >= EMOLUMENTS_DISCLOSURE_THRESHOLD:
        emit_anomaly(
            metric="emolument_detected",
            baseline=EMOLUMENTS_DISCLOSURE_THRESHOLD,
            delta=amount - EMOLUMENTS_DISCLOSURE_THRESHOLD,
            classification="violation",
            action="alert"
        )

    return emit_receipt("emolument_assessment", {
        "tenant_id": TENANT_ID,
        "payment_id": payment.get("id", "unknown"),
        "amount": amount,
        "source_name": source.get("name", "unknown"),
        "source_country": source.get("country", "unknown"),
        "is_foreign": is_foreign,
        "is_government": is_government,
        "is_emolument": is_emolument,
        "disclosure_threshold": EMOLUMENTS_DISCLOSURE_THRESHOLD,
        "exceeds_threshold": amount >= EMOLUMENTS_DISCLOSURE_THRESHOLD,
        "messitte_standard": "almost anything of value from foreign governments",
    })


def track_foreign_government(payments: list, government: str) -> dict:
    """Track payments from specific foreign government. Emit government_tracking_receipt.

    Args:
        payments: List of payment records
        government: Government/country to track

    Returns:
        government_tracking_receipt
    """
    gov_lower = government.lower()
    matching = [p for p in payments
                if p.get("source_country", "").lower() == gov_lower or
                   p.get("source_name", "").lower() == gov_lower]

    total = sum(p.get("amount", 0) for p in matching)

    # Group by property/recipient
    by_property = {}
    for p in matching:
        prop = p.get("recipient_property", "unknown")
        if prop not in by_property:
            by_property[prop] = {"total": 0, "count": 0}
        by_property[prop]["total"] += p.get("amount", 0)
        by_property[prop]["count"] += 1

    return emit_receipt("government_tracking", {
        "tenant_id": TENANT_ID,
        "government": government,
        "payment_count": len(matching),
        "total_amount": total,
        "by_property": by_property,
        "properties_count": len(by_property),
        "exceeds_disclosure_threshold": total >= EMOLUMENTS_DISCLOSURE_THRESHOLD,
    })


def compute_exposure(payments: list) -> dict:
    """Compute total emoluments exposure. Emit exposure_receipt.

    Args:
        payments: List of all payments to analyze

    Returns:
        exposure_receipt
    """
    total_payments = len(payments)
    total_amount = sum(p.get("amount", 0) for p in payments)

    # Filter to emoluments
    emoluments = []
    for p in payments:
        source = p.get("source", {})
        is_foreign = source.get("country", "").lower() not in ["us", "usa", "united states"]
        is_government = source.get("is_government", False) or source.get("is_sovereign", False)

        if is_foreign and is_government:
            emoluments.append(p)

    emoluments_total = sum(p.get("amount", 0) for p in emoluments)

    # By country breakdown
    by_country = {}
    for p in emoluments:
        country = p.get("source", {}).get("country", "unknown")
        if country not in by_country:
            by_country[country] = 0
        by_country[country] += p.get("amount", 0)

    return emit_receipt("emoluments_exposure", {
        "tenant_id": TENANT_ID,
        "total_payments_analyzed": total_payments,
        "total_payment_amount": total_amount,
        "emolument_count": len(emoluments),
        "emoluments_total": emoluments_total,
        "emoluments_percentage": (emoluments_total / total_amount * 100) if total_amount > 0 else 0,
        "by_country": by_country,
        "countries_count": len(by_country),
        "crew_documented_baseline": 7_800_000,  # $7.8M minimum
        "estimated_upper_bound": 160_000_000,   # $160M estimated
    })
