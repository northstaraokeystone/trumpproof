"""GolfProof Sanctions Module

OFAC sanctions screening.

Receipts: screening_receipt, transaction_screen_receipt, sdn_flag_receipt
"""

from ..core import emit_receipt, TENANT_ID, emit_anomaly


def screen_entity(entity: dict, sdn_list: list = None) -> dict:
    """Screen entity against OFAC SDN list. Emit screening_receipt.

    Args:
        entity: Entity to screen
        sdn_list: SDN list entries (optional - would connect to OFAC API in prod)

    Returns:
        screening_receipt
    """
    sdn_list = sdn_list or []

    entity_name = entity.get("name", "").lower()
    entity_country = entity.get("country", "").lower()

    # Simple matching (in production, would use fuzzy matching)
    matches = []
    for sdn in sdn_list:
        sdn_name = sdn.get("name", "").lower()
        sdn_country = sdn.get("country", "").lower()

        if entity_name == sdn_name:
            matches.append(
                {
                    "sdn_id": sdn.get("id"),
                    "sdn_name": sdn.get("name"),
                    "match_type": "exact_name",
                    "confidence": 1.0,
                }
            )
        elif entity_country == sdn_country and entity_country in [
            "russia",
            "iran",
            "north korea",
            "syria",
            "cuba",
        ]:
            matches.append(
                {
                    "sdn_id": sdn.get("id"),
                    "sdn_name": sdn.get("name"),
                    "match_type": "high_risk_country",
                    "confidence": 0.5,
                }
            )

    return emit_receipt(
        "sanctions_screening",
        {
            "tenant_id": TENANT_ID,
            "entity_id": entity.get("id", "unknown"),
            "entity_name": entity.get("name", "unknown"),
            "entity_country": entity.get("country", "unknown"),
            "sdn_entries_checked": len(sdn_list),
            "matches_found": len(matches),
            "matches": matches,
            "cleared": len(matches) == 0,
            "requires_review": len(matches) > 0,
        },
    )


def screen_transaction(transaction: dict, sdn_list: list = None) -> dict:
    """Screen transaction for sanctions exposure. Emit transaction_screen_receipt.

    Args:
        transaction: Transaction to screen
        sdn_list: SDN list entries

    Returns:
        transaction_screen_receipt
    """
    sdn_list = sdn_list or []

    # Screen both parties
    sender = transaction.get("sender", {})
    recipient = transaction.get("recipient", {})

    sender_screen = screen_entity(sender, sdn_list)
    recipient_screen = screen_entity(recipient, sdn_list)

    blocked = not sender_screen.get("cleared", True) or not recipient_screen.get(
        "cleared", True
    )

    return emit_receipt(
        "transaction_screening",
        {
            "tenant_id": TENANT_ID,
            "transaction_id": transaction.get("id", "unknown"),
            "amount": transaction.get("amount", 0),
            "sender_cleared": sender_screen.get("cleared", True),
            "recipient_cleared": recipient_screen.get("cleared", True),
            "blocked": blocked,
            "sender_matches": sender_screen.get("matches", []),
            "recipient_matches": recipient_screen.get("matches", []),
        },
    )


def flag_match(entity_id: str, sdn_match: dict) -> dict:
    """Flag potential SDN match. Emit sdn_flag_receipt.

    Args:
        entity_id: Entity identifier
        sdn_match: SDN match details

    Returns:
        sdn_flag_receipt
    """
    # Emit anomaly for tracking
    emit_anomaly(
        metric="sdn_match",
        baseline=0,
        delta=1,
        classification="violation",
        action="halt",
    )

    confidence = sdn_match.get("confidence", 0)
    severity = (
        "critical"
        if confidence >= 0.9
        else "high"
        if confidence >= 0.7
        else "medium"
        if confidence >= 0.5
        else "low"
    )

    return emit_receipt(
        "sdn_flag",
        {
            "tenant_id": TENANT_ID,
            "entity_id": entity_id,
            "sdn_id": sdn_match.get("sdn_id", "unknown"),
            "sdn_name": sdn_match.get("sdn_name", "unknown"),
            "match_type": sdn_match.get("match_type", "unknown"),
            "confidence": confidence,
            "severity": severity,
            "action_required": "IMMEDIATE_REVIEW"
            if severity in ["critical", "high"]
            else "REVIEW",
            "blocked": severity in ["critical", "high"],
        },
    )
