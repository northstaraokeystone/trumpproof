"""LicenseProof Partner Module

International partner tracking.

Key Partners:
- Dar Global (Dar Al Arkan subsidiary): Trump Tower Jeddah, Trump Plaza Jeddah,
  Trump International Oman

Key Projects:
- $533M Trump Tower Jeddah (Dec 2024)
- $1B Trump Plaza Jeddah (Sept 2025)
- $500M Trump International Oman (opens Dec 2028)

Receipts: partner_receipt, government_ties_receipt, pif_cross_ref_receipt
"""

from ..core import emit_receipt, dual_hash, TENANT_ID
from ..constants import GULF_PIF_INVESTMENT, GOLF_LIV_PIF_INVESTMENT


def register_partner(partner: dict, country: str) -> dict:
    """Register international partner. Emit partner_receipt.

    Args:
        partner: Partner entity details
        country: Partner's country

    Returns:
        partner_receipt
    """
    return emit_receipt("partner_registration", {
        "tenant_id": TENANT_ID,
        "partner_id": partner.get("id", dual_hash(str(partner))[:12]),
        "partner_name": partner.get("name", "unknown"),
        "country": country,
        "parent_company": partner.get("parent_company", None),
        "projects": partner.get("projects", []),
        "total_project_value": sum(p.get("value", 0) for p in partner.get("projects", [])),
        "relationship_start": partner.get("relationship_start", "unknown"),
    })


def assess_government_ties(partner_id: str, partner: dict = None) -> dict:
    """Assess partner's government ties. Emit government_ties_receipt.

    Args:
        partner_id: Partner identifier
        partner: Partner details (optional)

    Returns:
        government_ties_receipt
    """
    partner = partner or {}

    ties = []

    if partner.get("state_owned"):
        ties.append({
            "type": "state_owned",
            "description": "Partner is state-owned enterprise",
        })

    if partner.get("government_contracts"):
        ties.append({
            "type": "government_contracts",
            "value": partner.get("government_contract_value", 0),
        })

    if partner.get("royal_family_connection"):
        ties.append({
            "type": "royal_family",
            "description": partner.get("royal_connection_details", "unknown"),
        })

    if partner.get("swf_investment"):
        ties.append({
            "type": "swf_investment",
            "fund": partner.get("swf_name", "unknown"),
            "amount": partner.get("swf_investment_amount", 0),
        })

    risk_level = "high" if len(ties) >= 2 else "medium" if ties else "low"

    return emit_receipt("government_ties", {
        "tenant_id": TENANT_ID,
        "partner_id": partner_id,
        "partner_name": partner.get("name", "unknown"),
        "country": partner.get("country", "unknown"),
        "ties": ties,
        "tie_count": len(ties),
        "risk_level": risk_level,
    })


def cross_reference_pif(partner: dict) -> dict:
    """Cross-reference with Saudi PIF ecosystem. Emit pif_cross_ref_receipt.

    Saudi PIF is central node across domains:
    - Gulf: $2B to Kushner's Affinity
    - Golf: $4.58B to LIV Golf
    - License: Building Trump towers via Dar Global

    Args:
        partner: Partner to cross-reference

    Returns:
        pif_cross_ref_receipt
    """
    pif_connections = []

    # Direct PIF investment
    if partner.get("pif_investment"):
        pif_connections.append({
            "type": "direct_investment",
            "amount": partner.get("pif_investment_amount", 0),
        })

    # PIF-connected parent company
    parent = partner.get("parent_company", "").lower()
    if "dar" in parent or "arkan" in parent:
        pif_connections.append({
            "type": "pif_ecosystem",
            "entity": partner.get("parent_company"),
            "connection": "Dar Al Arkan / Dar Global",
        })

    # Saudi government connection (implies PIF connection)
    if partner.get("country", "").lower() == "saudi arabia" and partner.get("government_ties"):
        pif_connections.append({
            "type": "saudi_government",
            "description": "Saudi government ties imply PIF connection potential",
        })

    is_pif_connected = len(pif_connections) > 0

    return emit_receipt("pif_cross_reference", {
        "tenant_id": TENANT_ID,
        "partner_id": partner.get("id", dual_hash(str(partner))[:12]),
        "partner_name": partner.get("name", "unknown"),
        "pif_connections": pif_connections,
        "is_pif_connected": is_pif_connected,
        "pif_connection_count": len(pif_connections),
        # Cross-domain PIF exposure
        "pif_gulf_exposure": GULF_PIF_INVESTMENT,  # $2B Kushner
        "pif_golf_exposure": GOLF_LIV_PIF_INVESTMENT,  # $4.58B LIV
        "pif_total_documented": GULF_PIF_INVESTMENT + GOLF_LIV_PIF_INVESTMENT,
    })
