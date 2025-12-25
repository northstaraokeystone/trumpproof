"""Loop Cross-Domain Module

Pattern detection across all five modules.

Receipts: overlap_receipt, flow_receipt, centrality_receipt, pif_connection_receipt
"""

from ..core import emit_receipt, TENANT_ID
from ..constants import (
    GULF_PIF_INVESTMENT,
    GOLF_LIV_PIF_INVESTMENT,
    PIF_TOTAL_EXPOSURE,
)


def detect_entity_overlap(modules: dict) -> dict:
    """Detect entities appearing across modules. Emit overlap_receipt.

    Args:
        modules: Dict of module_name -> list of receipts

    Returns:
        overlap_receipt with entity overlaps
    """
    # Extract entities from each module
    entity_modules = {}

    for module_name, receipts in modules.items():
        for r in receipts:
            # Extract entity identifiers from various fields
            entities = extract_entities(r)
            for entity in entities:
                if entity not in entity_modules:
                    entity_modules[entity] = set()
                entity_modules[entity].add(module_name)

    # Find entities appearing in multiple modules
    overlaps = []
    for entity, module_set in entity_modules.items():
        if len(module_set) >= 2:
            overlaps.append({
                "entity": entity,
                "modules": list(module_set),
                "module_count": len(module_set),
            })

    # Sort by module count (most cross-domain first)
    overlaps.sort(key=lambda x: x["module_count"], reverse=True)

    return emit_receipt("entity_overlap", {
        "tenant_id": TENANT_ID,
        "modules_analyzed": list(modules.keys()),
        "total_entities": len(entity_modules),
        "overlapping_entities": len(overlaps),
        "overlaps": overlaps[:50],  # Top 50
        "max_overlap": overlaps[0]["module_count"] if overlaps else 0,
    })


def extract_entities(receipt: dict) -> list:
    """Extract entity identifiers from receipt."""
    entities = []

    # Check various entity fields
    entity_fields = [
        "entity_id", "entity_name", "applicant", "contractor_id", "contractor_name",
        "partner_id", "partner_name", "source_name", "recipient_name",
        "fund_id", "fund_name", "licensor_name", "licensee_name"
    ]

    for field in entity_fields:
        if field in receipt and receipt[field]:
            entities.append(str(receipt[field]).lower())

    return entities


def trace_money_flow(entity_id: str, receipts: list) -> dict:
    """Trace money flow across modules. Emit flow_receipt.

    Args:
        entity_id: Entity to trace
        receipts: All receipts to search

    Returns:
        flow_receipt with money flow trace
    """
    flows = []
    total_inflow = 0
    total_outflow = 0

    entity_lower = entity_id.lower()

    for r in receipts:
        # Check if entity is involved
        entities = extract_entities(r)
        if entity_lower not in entities:
            continue

        # Extract money flow
        amount = (
            r.get("amount", 0) or
            r.get("payment_amount", 0) or
            r.get("fee_amount", 0) or
            r.get("contract_value", 0) or
            0
        )

        if amount > 0:
            direction = determine_flow_direction(r, entity_lower)
            flows.append({
                "receipt_type": r.get("receipt_type"),
                "amount": amount,
                "direction": direction,
                "counterparty": get_counterparty(r, entity_lower),
                "module": infer_module(r.get("receipt_type", "")),
            })

            if direction == "inflow":
                total_inflow += amount
            else:
                total_outflow += amount

    return emit_receipt("money_flow", {
        "tenant_id": TENANT_ID,
        "entity_id": entity_id,
        "total_inflow": total_inflow,
        "total_outflow": total_outflow,
        "net_flow": total_inflow - total_outflow,
        "flow_count": len(flows),
        "flows": flows,
    })


def determine_flow_direction(receipt: dict, entity: str) -> str:
    """Determine if money flows in or out for entity."""
    recipient = str(receipt.get("recipient_name", "")).lower()
    if entity in recipient:
        return "inflow"
    return "outflow"


def get_counterparty(receipt: dict, entity: str) -> str:
    """Get counterparty in transaction."""
    source = str(receipt.get("source_name", "")).lower()
    recipient = str(receipt.get("recipient_name", "")).lower()

    if entity in recipient:
        return source
    return recipient


def infer_module(receipt_type: str) -> str:
    """Infer module from receipt type."""
    type_lower = receipt_type.lower()
    if "tariff" in type_lower:
        return "tariff"
    elif "detention" in type_lower or "border" in type_lower:
        return "border"
    elif "swf" in type_lower or "fara" in type_lower:
        return "gulf"
    elif "golf" in type_lower or "emolument" in type_lower:
        return "golf"
    elif "license" in type_lower:
        return "license"
    return "unknown"


def compute_centrality(entities: list, receipts: list) -> dict:
    """Compute entity centrality score. Emit centrality_receipt.

    Centrality = how connected an entity is across modules and transactions.

    Args:
        entities: List of entities to analyze
        receipts: All receipts

    Returns:
        centrality_receipt with scores
    """
    scores = []

    for entity in entities:
        entity_lower = entity.lower()
        connections = 0
        modules_touched = set()
        total_value = 0

        for r in receipts:
            extracted = extract_entities(r)
            if entity_lower in extracted:
                connections += 1
                modules_touched.add(infer_module(r.get("receipt_type", "")))
                total_value += (
                    r.get("amount", 0) or
                    r.get("payment_amount", 0) or
                    0
                )

        # Centrality score: connections * modules * log(value + 1)
        import math
        centrality = connections * len(modules_touched) * math.log10(total_value + 1)

        scores.append({
            "entity": entity,
            "connections": connections,
            "modules": list(modules_touched),
            "module_count": len(modules_touched),
            "total_value": total_value,
            "centrality_score": centrality,
        })

    # Sort by centrality
    scores.sort(key=lambda x: x["centrality_score"], reverse=True)

    return emit_receipt("centrality", {
        "tenant_id": TENANT_ID,
        "entities_analyzed": len(entities),
        "scores": scores,
        "most_central": scores[0] if scores else None,
    })


def flag_pif_connection(entity: dict) -> dict:
    """Flag Saudi PIF connections. Emit pif_connection_receipt.

    Saudi PIF is central node across domains:
    - Gulf: $2B to Kushner's Affinity
    - Golf: $4.58B to LIV Golf
    - License: Building Trump towers via Dar Global

    Args:
        entity: Entity to check

    Returns:
        pif_connection_receipt
    """
    pif_indicators = []

    entity_name = entity.get("name", "").lower()
    entity_country = entity.get("country", "").lower()

    # Direct PIF connection
    if "pif" in entity_name or "public investment fund" in entity_name:
        pif_indicators.append("direct_pif_entity")

    # Saudi government connection
    if entity_country == "saudi arabia":
        if entity.get("is_government") or entity.get("government_ties"):
            pif_indicators.append("saudi_government")

    # Known PIF-connected entities
    pif_entities = ["affinity", "liv golf", "dar global", "dar al arkan"]
    for pif_entity in pif_entities:
        if pif_entity in entity_name:
            pif_indicators.append(f"known_pif_connected:{pif_entity}")

    is_pif_connected = len(pif_indicators) > 0

    return emit_receipt("pif_connection", {
        "tenant_id": TENANT_ID,
        "entity_id": entity.get("id", "unknown"),
        "entity_name": entity.get("name", "unknown"),
        "pif_indicators": pif_indicators,
        "is_pif_connected": is_pif_connected,
        "pif_total_exposure": PIF_TOTAL_EXPOSURE,
        "domains": ["gulf", "golf", "license"] if is_pif_connected else [],
    })
