"""LicenseProof Ownership Module

Beneficial ownership resolution (despite CTA gutting).

Infrastructure Gutted:
- Treasury March 2025 interim rule exempted ALL U.S. domestic entities
- Eliminated infrastructure requiring disclosure

Track despite gutting - document what should be disclosed.

Receipts: ownership_receipt, shell_receipt, opacity_flag_receipt
"""

from ..core import emit_receipt, dual_hash, TENANT_ID
from ..constants import OPACITY_CRITICAL


def resolve_ownership(entity: dict, depth: int = 5) -> dict:
    """Resolve beneficial ownership chain. Emit ownership_receipt.

    Args:
        entity: Entity to resolve
        depth: Maximum resolution depth

    Returns:
        ownership_receipt
    """
    ownership_chain = []
    current = entity
    resolved_depth = 0

    for i in range(depth):
        if not current:
            break

        owner = current.get("parent_entity")
        ownership_chain.append(
            {
                "level": i,
                "entity_name": current.get("name", "unknown"),
                "entity_type": current.get("type", "unknown"),
                "jurisdiction": current.get("jurisdiction", "unknown"),
                "ownership_percentage": current.get("ownership_percentage", 100),
            }
        )

        if owner:
            current = owner
            resolved_depth = i + 1
        else:
            break

    # Check for beneficial owner identification
    ultimate_owner = ownership_chain[-1] if ownership_chain else None
    owner_identified = (
        ultimate_owner and ultimate_owner.get("entity_type") == "individual"
    )

    return emit_receipt(
        "ownership_resolution",
        {
            "tenant_id": TENANT_ID,
            "entity_id": entity.get("id", dual_hash(str(entity))[:12]),
            "entity_name": entity.get("name", "unknown"),
            "ownership_chain": ownership_chain,
            "resolution_depth": resolved_depth,
            "max_depth": depth,
            "ultimate_owner": ultimate_owner,
            "owner_identified": owner_identified,
            "cta_exempt": True,  # All US entities now exempt per March 2025 rule
            "should_be_disclosed": True,  # Track what should be disclosed
        },
    )


def track_shell_company(entity: dict, jurisdiction: str) -> dict:
    """Track shell company structure. Emit shell_receipt.

    Args:
        entity: Entity to track
        jurisdiction: Entity's jurisdiction

    Returns:
        shell_receipt
    """
    # Shell company indicators
    indicators = []

    if jurisdiction.lower() in [
        "delaware",
        "nevada",
        "wyoming",
        "british virgin islands",
        "cayman islands",
        "panama",
        "luxembourg",
    ]:
        indicators.append("favorable_jurisdiction")

    if entity.get("no_employees", False) or entity.get("employees", 0) == 0:
        indicators.append("no_employees")

    if entity.get("registered_agent_only", False):
        indicators.append("registered_agent_address")

    if not entity.get("physical_operations"):
        indicators.append("no_physical_operations")

    if entity.get("nominee_directors", False):
        indicators.append("nominee_directors")

    shell_score = len(indicators) / 5  # 5 possible indicators

    return emit_receipt(
        "shell_company",
        {
            "tenant_id": TENANT_ID,
            "entity_id": entity.get("id", dual_hash(str(entity))[:12]),
            "entity_name": entity.get("name", "unknown"),
            "jurisdiction": jurisdiction,
            "indicators": indicators,
            "indicator_count": len(indicators),
            "shell_score": shell_score,
            "likely_shell": shell_score >= 0.6,
        },
    )


def flag_opacity(entity_id: str, unresolved_layers: int) -> dict:
    """Flag ownership opacity. Emit opacity_flag_receipt.

    Args:
        entity_id: Entity identifier
        unresolved_layers: Number of unresolved ownership layers

    Returns:
        opacity_flag_receipt
    """
    # Opacity score based on unresolved layers
    opacity_score = min(1.0, unresolved_layers / 5)  # 5+ layers = max opacity

    severity = (
        "critical"
        if opacity_score >= OPACITY_CRITICAL
        else "high"
        if opacity_score >= 0.6
        else "medium"
        if opacity_score >= 0.4
        else "low"
    )

    return emit_receipt(
        "opacity_flag",
        {
            "tenant_id": TENANT_ID,
            "entity_id": entity_id,
            "unresolved_layers": unresolved_layers,
            "opacity_score": opacity_score,
            "severity": severity,
            "threshold_critical": OPACITY_CRITICAL,
            "cta_would_require_disclosure": True,
            "cta_status": "gutted_march_2025",
        },
    )
