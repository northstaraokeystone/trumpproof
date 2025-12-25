"""GolfProof Payment Module

Foreign payment attestation.

Key Data:
- Trump World Tower: $1.95M from Saudi/Qatar/India/Afghanistan/Kuwait in condo charges
- CREW documented $7.8M minimum from 20+ foreign governments
- Up to $160M total estimated

Receipts: payment_receipt, classification_receipt, country_aggregate_receipt
"""

from ..core import emit_receipt, dual_hash, TENANT_ID
from ..constants import GOLF_ANNUAL_REVENUE


def register_payment(source: dict, recipient: dict, amount: float) -> dict:
    """Register payment with source verification. Emit payment_receipt.

    Args:
        source: Payment source details
        recipient: Payment recipient details
        amount: Payment amount

    Returns:
        payment_receipt
    """
    return emit_receipt("payment", {
        "tenant_id": TENANT_ID,
        "payment_id": dual_hash(f"{source}{recipient}{amount}")[:16],
        "source_name": source.get("name", "unknown"),
        "source_country": source.get("country", "unknown"),
        "source_type": source.get("type", "unknown"),
        "recipient_name": recipient.get("name", "unknown"),
        "recipient_property": recipient.get("property", "unknown"),
        "amount": amount,
        "payment_date": source.get("date", "unknown"),
        "verified": source.get("verified", False),
    })


def classify_source(source: dict) -> dict:
    """Classify source (domestic/foreign/government/SWF). Emit classification_receipt.

    Args:
        source: Source to classify

    Returns:
        classification_receipt
    """
    country = source.get("country", "").lower()
    source_type = source.get("type", "").lower()

    # Classification logic
    if country in ["us", "usa", "united states"]:
        location = "domestic"
    else:
        location = "foreign"

    if "government" in source_type or source.get("is_government", False):
        entity_type = "government"
    elif "sovereign" in source_type or "swf" in source_type or source.get("is_swf", False):
        entity_type = "sovereign_wealth_fund"
    elif source.get("is_state_owned", False):
        entity_type = "state_owned_enterprise"
    else:
        entity_type = "private"

    # Emoluments concern if foreign government or SWF
    emoluments_concern = location == "foreign" and entity_type in [
        "government", "sovereign_wealth_fund", "state_owned_enterprise"
    ]

    return emit_receipt("source_classification", {
        "tenant_id": TENANT_ID,
        "source_id": source.get("id", dual_hash(str(source))[:12]),
        "source_name": source.get("name", "unknown"),
        "country": source.get("country", "unknown"),
        "location_classification": location,
        "entity_type": entity_type,
        "emoluments_concern": emoluments_concern,
    })


def aggregate_by_country(payments: list) -> dict:
    """Aggregate payments by country. Emit country_aggregate_receipt.

    Args:
        payments: List of payment records

    Returns:
        country_aggregate_receipt
    """
    by_country = {}
    by_type = {"domestic": 0, "foreign": 0, "government": 0, "swf": 0}

    for p in payments:
        country = p.get("source_country", "unknown")
        amount = p.get("amount", 0)
        source_type = p.get("source_type", "unknown").lower()

        if country not in by_country:
            by_country[country] = {"total": 0, "count": 0, "payments": []}

        by_country[country]["total"] += amount
        by_country[country]["count"] += 1
        by_country[country]["payments"].append(p)

        # Type aggregation
        if country.lower() in ["us", "usa", "united states"]:
            by_type["domestic"] += amount
        else:
            by_type["foreign"] += amount

        if "government" in source_type:
            by_type["government"] += amount
        if "swf" in source_type or "sovereign" in source_type:
            by_type["swf"] += amount

    # Top countries
    sorted_countries = sorted(
        by_country.items(),
        key=lambda x: x[1]["total"],
        reverse=True
    )
    top_countries = [
        {"country": c, "total": d["total"], "count": d["count"]}
        for c, d in sorted_countries[:10]
    ]

    return emit_receipt("country_aggregate", {
        "tenant_id": TENANT_ID,
        "total_payments": len(payments),
        "total_amount": sum(p.get("amount", 0) for p in payments),
        "countries_count": len(by_country),
        "by_country": {k: {"total": v["total"], "count": v["count"]}
                       for k, v in by_country.items()},
        "by_type": by_type,
        "top_countries": top_countries,
        "foreign_government_total": by_type["government"],
        "crew_documented_baseline": 7_800_000,  # $7.8M minimum documented
    })
