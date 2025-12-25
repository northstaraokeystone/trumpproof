"""Loop PIF Tracker Module

Saudi PIF central node monitoring across all domains.

Cross-Domain PIF Connections:
- GulfProof: $2B direct investment in Kushner's Affinity
- GolfProof: 93% LIV Golf ownership, events at Trump properties
- LicenseProof: Dar Al Arkan building Trump towers
- TariffProof: PIF affected by trade policy (EA acquisition subject to CFIUS)

Receipts: pif_entity_receipt, pif_aggregate_receipt, pif_pattern_receipt
"""

from ..core import emit_receipt, TENANT_ID
from ..constants import (
    GULF_PIF_INVESTMENT,
    GOLF_LIV_PIF_INVESTMENT,
    GULF_AFFINITY_AUM,
    GULF_FEES_COLLECTED,
    PIF_TOTAL_EXPOSURE,
)


# Known PIF-connected entities
PIF_CONNECTED_ENTITIES = {
    "affinity partners": {
        "domain": "gulf",
        "investment": GULF_PIF_INVESTMENT,
        "relationship": "direct_investment",
    },
    "liv golf": {
        "domain": "golf",
        "investment": GOLF_LIV_PIF_INVESTMENT,
        "relationship": "93%_ownership",
    },
    "dar global": {
        "domain": "license",
        "investment": 0,  # Licensing, not investment
        "relationship": "development_partner",
    },
    "dar al arkan": {
        "domain": "license",
        "investment": 0,
        "relationship": "parent_of_dar_global",
    },
}


def track_pif_entity(entity: dict, domain: str) -> dict:
    """Track PIF-connected entity by domain. Emit pif_entity_receipt.

    Args:
        entity: Entity details
        domain: Domain where entity appears

    Returns:
        pif_entity_receipt
    """
    entity_name = entity.get("name", "").lower()

    # Check if known PIF entity
    known_connection = None
    for known_entity, details in PIF_CONNECTED_ENTITIES.items():
        if known_entity in entity_name:
            known_connection = {"known_entity": known_entity, **details}
            break

    return emit_receipt(
        "pif_entity",
        {
            "tenant_id": TENANT_ID,
            "entity_id": entity.get("id", "unknown"),
            "entity_name": entity.get("name", "unknown"),
            "domain": domain,
            "known_connection": known_connection,
            "is_known_pif_entity": known_connection is not None,
            "pif_investment": known_connection["investment"] if known_connection else 0,
        },
    )


def aggregate_pif_exposure() -> dict:
    """Aggregate PIF exposure across all domains. Emit pif_aggregate_receipt.

    Returns:
        pif_aggregate_receipt with total exposure
    """
    by_domain = {
        "gulf": {
            "entities": ["Affinity Partners"],
            "direct_investment": GULF_PIF_INVESTMENT,
            "aum_managed": GULF_AFFINITY_AUM,
            "fees_paid": GULF_FEES_COLLECTED,
            "relationship": "LP investment",
        },
        "golf": {
            "entities": ["LIV Golf"],
            "direct_investment": GOLF_LIV_PIF_INVESTMENT,
            "ownership_percentage": 93,
            "relationship": "93% ownership",
        },
        "license": {
            "entities": ["Dar Global", "Dar Al Arkan"],
            "direct_investment": 0,
            "project_value": 2_033_000_000,  # $533M + $1B + $500M
            "relationship": "Development partnerships",
        },
        "tariff": {
            "entities": ["EA (Electronic Arts)"],
            "direct_investment": 0,
            "cfius_exposure": True,
            "relationship": "Trade policy affected",
        },
    }

    total_direct = sum(d.get("direct_investment", 0) for d in by_domain.values())
    domains_with_exposure = len(
        [
            d
            for d in by_domain.values()
            if d.get("direct_investment", 0) > 0
            or d.get("project_value", 0) > 0
            or d.get("cfius_exposure")
        ]
    )

    return emit_receipt(
        "pif_aggregate",
        {
            "tenant_id": TENANT_ID,
            "by_domain": by_domain,
            "domain_count": domains_with_exposure,
            "total_direct_investment": total_direct,
            "total_exposure": PIF_TOTAL_EXPOSURE,
            "cross_domain_verified": domains_with_exposure >= 4,
        },
    )


def detect_pif_pattern(receipts: list) -> dict:
    """Detect patterns in PIF connections. Emit pif_pattern_receipt.

    Args:
        receipts: All receipts to analyze

    Returns:
        pif_pattern_receipt
    """
    patterns = []

    # Track PIF mentions across receipts
    pif_receipts = []
    for r in receipts:
        # Check for PIF-related content
        r_str = str(r).lower()
        if (
            "pif" in r_str
            or "saudi" in r_str
            or any(entity in r_str for entity in PIF_CONNECTED_ENTITIES)
        ):
            pif_receipts.append(r)

    # Pattern: Same PIF entity in multiple domains
    entity_domains = {}
    for r in pif_receipts:
        receipt_type = r.get("receipt_type", "").lower()
        domain = infer_domain(receipt_type)
        entities = extract_pif_entities(r)

        for entity in entities:
            if entity not in entity_domains:
                entity_domains[entity] = set()
            entity_domains[entity].add(domain)

    for entity, domains in entity_domains.items():
        if len(domains) >= 2:
            patterns.append(
                {
                    "type": "cross_domain_pif_entity",
                    "entity": entity,
                    "domains": list(domains),
                    "domain_count": len(domains),
                }
            )

    # Pattern: Money flow through PIF ecosystem
    total_pif_flow = sum(
        r.get("amount", 0) or r.get("pif_investment", 0) or 0 for r in pif_receipts
    )
    if total_pif_flow > 1_000_000_000:  # $1B+
        patterns.append(
            {
                "type": "significant_pif_flow",
                "total_value": total_pif_flow,
                "threshold": 1_000_000_000,
            }
        )

    return emit_receipt(
        "pif_pattern",
        {
            "tenant_id": TENANT_ID,
            "receipts_analyzed": len(receipts),
            "pif_related_receipts": len(pif_receipts),
            "patterns_detected": len(patterns),
            "patterns": patterns,
            "central_node_confirmed": len(patterns) >= 2,
        },
    )


def infer_domain(receipt_type: str) -> str:
    """Infer domain from receipt type."""
    if "tariff" in receipt_type or "exemption" in receipt_type:
        return "tariff"
    elif "detention" in receipt_type or "border" in receipt_type:
        return "border"
    elif (
        "swf" in receipt_type or "fara" in receipt_type or "investment" in receipt_type
    ):
        return "gulf"
    elif "golf" in receipt_type or "liv" in receipt_type or "emolument" in receipt_type:
        return "golf"
    elif "license" in receipt_type or "ownership" in receipt_type:
        return "license"
    return "unknown"


def extract_pif_entities(receipt: dict) -> list:
    """Extract PIF-related entities from receipt."""
    entities = []
    r_str = str(receipt).lower()

    for known_entity in PIF_CONNECTED_ENTITIES:
        if known_entity in r_str:
            entities.append(known_entity)

    return entities
