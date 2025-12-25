"""TariffProof Lobby Module

Cross-reference exemption outcomes with lobbying disclosure.
Receipts: lda_receipt, cross_ref_receipt, pattern_receipt
"""

from ..core import emit_receipt, dual_hash, TENANT_ID


def ingest_lda_filings(filings: list) -> dict:
    """Ingest Lobbying Disclosure Act filings. Emit lda_receipt.

    Args:
        filings: List of LDA filing records

    Returns:
        lda_receipt with filing summary
    """
    total_spend = sum(f.get("amount", 0) for f in filings)
    clients = set(f.get("client", "") for f in filings if f.get("client"))
    lobbyists = set(f.get("lobbyist", "") for f in filings if f.get("lobbyist"))
    issues = set()
    for f in filings:
        for issue in f.get("issues", []):
            issues.add(issue)

    return emit_receipt(
        "lda_ingest",
        {
            "tenant_id": TENANT_ID,
            "filing_count": len(filings),
            "total_spend": total_spend,
            "unique_clients": len(clients),
            "unique_lobbyists": len(lobbyists),
            "tariff_related_issues": [i for i in issues if "tariff" in i.lower()],
            "data_hash": dual_hash(str(filings)),
        },
    )


def cross_reference(exemptions: list, lda_filings: list) -> dict:
    """Cross-reference exemptions with lobbyists. Emit cross_ref_receipt.

    Args:
        exemptions: List of exemption records
        lda_filings: List of LDA filings

    Returns:
        cross_ref_receipt with matches
    """
    # Build client lookup from LDA filings
    client_to_lobbyist = {}
    client_to_spend = {}

    for filing in lda_filings:
        client = filing.get("client", "").lower()
        if client:
            lobbyist = filing.get("lobbyist", "")
            amount = filing.get("amount", 0)
            if client not in client_to_lobbyist:
                client_to_lobbyist[client] = []
                client_to_spend[client] = 0
            client_to_lobbyist[client].append(lobbyist)
            client_to_spend[client] += amount

    # Cross-reference with exemptions
    matches = []
    for ex in exemptions:
        applicant = ex.get("applicant", "").lower()
        if applicant in client_to_lobbyist:
            matches.append(
                {
                    "exemption_id": ex.get("id", "unknown"),
                    "applicant": applicant,
                    "outcome": ex.get("outcome", "unknown"),
                    "lobbyists": client_to_lobbyist[applicant],
                    "total_lobbying_spend": client_to_spend[applicant],
                }
            )

    return emit_receipt(
        "exemption_lobbying_cross_ref",
        {
            "tenant_id": TENANT_ID,
            "exemptions_analyzed": len(exemptions),
            "lda_filings_analyzed": len(lda_filings),
            "matches_found": len(matches),
            "match_rate": len(matches) / len(exemptions) if exemptions else 0,
            "matches": matches,
        },
    )


def detect_pattern(cross_refs: list) -> dict:
    """Detect suspicious patterns. Emit pattern_receipt.

    Patterns detected:
    - High-spend lobbyists with high approval rates
    - Clustered approvals around lobbying dates
    - Repeat approvals for same entities

    Args:
        cross_refs: List of cross-reference results

    Returns:
        pattern_receipt with detected patterns
    """
    patterns = []

    # Analyze spend vs outcome correlation
    approved_spend = []
    denied_spend = []

    for ref in cross_refs:
        spend = ref.get("total_lobbying_spend", 0)
        outcome = ref.get("outcome", "")
        if outcome == "approved":
            approved_spend.append(spend)
        elif outcome == "denied":
            denied_spend.append(spend)

    avg_approved_spend = (
        sum(approved_spend) / len(approved_spend) if approved_spend else 0
    )
    avg_denied_spend = sum(denied_spend) / len(denied_spend) if denied_spend else 0

    if avg_approved_spend > avg_denied_spend * 2:
        patterns.append(
            {
                "type": "spend_correlation",
                "description": "Approved exemptions average 2x+ lobbying spend vs denied",
                "avg_approved_spend": avg_approved_spend,
                "avg_denied_spend": avg_denied_spend,
                "ratio": avg_approved_spend / avg_denied_spend
                if avg_denied_spend
                else float("inf"),
            }
        )

    # Detect repeat approvals
    entity_approvals = {}
    for ref in cross_refs:
        entity = ref.get("applicant", "")
        if ref.get("outcome") == "approved":
            entity_approvals[entity] = entity_approvals.get(entity, 0) + 1

    repeat_approvals = {k: v for k, v in entity_approvals.items() if v > 1}
    if repeat_approvals:
        patterns.append(
            {
                "type": "repeat_approvals",
                "description": "Entities receiving multiple exemption approvals",
                "entities": repeat_approvals,
                "total_repeat_count": sum(repeat_approvals.values()),
            }
        )

    return emit_receipt(
        "lobbying_pattern",
        {
            "tenant_id": TENANT_ID,
            "cross_refs_analyzed": len(cross_refs),
            "patterns_detected": len(patterns),
            "patterns": patterns,
            "risk_level": "high"
            if len(patterns) >= 2
            else "medium"
            if patterns
            else "low",
        },
    )
