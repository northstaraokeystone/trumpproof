"""BorderProof Contractor Module

Contractor accountability and cost-per-outcome tracking.

Key Metrics:
- GEO Group + CoreCivic donated $3M+ to Trump entities
- Class-action lawsuit: California City facility described as "torture chamber"
- Fort Bliss violated 60+ federal detention standards in first 50 days

Conflict Documentation:
- Homan received $5K+ consulting fees from GEO Group pre-appointment
- Allegedly hired former GEO Group exec as No. 2
- FBI investigation closed Sept 2025 (insufficient evidence)

Receipts: contractor_receipt, contract_receipt, outcome_receipt, donation_cross_ref_receipt
"""

from ..core import emit_receipt, dual_hash, TENANT_ID


def register_contractor(contractor: dict) -> dict:
    """Register contractor with donation history. Emit contractor_receipt.

    Args:
        contractor: Contractor details including donation history

    Returns:
        contractor_receipt
    """
    donations = contractor.get("donations", [])
    total_donations = sum(d.get("amount", 0) for d in donations)
    trump_entity_donations = sum(
        d.get("amount", 0)
        for d in donations
        if "trump" in d.get("recipient", "").lower()
    )

    return emit_receipt(
        "contractor_registration",
        {
            "tenant_id": TENANT_ID,
            "contractor_id": contractor.get("id", dual_hash(str(contractor))[:12]),
            "contractor_name": contractor.get("name", "unknown"),
            "contractor_type": contractor.get("type", "unknown"),
            "total_donations": total_donations,
            "trump_entity_donations": trump_entity_donations,
            "donation_history": donations,
            "is_major_donor": total_donations > 100_000,
        },
    )


def track_contract(contractor_id: str, contract: dict) -> dict:
    """Track contract terms and performance. Emit contract_receipt.

    Args:
        contractor_id: Contractor identifier
        contract: Contract details

    Returns:
        contract_receipt
    """
    return emit_receipt(
        "contract_tracking",
        {
            "tenant_id": TENANT_ID,
            "contractor_id": contractor_id,
            "contract_id": contract.get("id", "unknown"),
            "contract_value": contract.get("value", 0),
            "start_date": contract.get("start_date", "unknown"),
            "end_date": contract.get("end_date", "unknown"),
            "facility_count": contract.get("facility_count", 0),
            "bed_capacity": contract.get("bed_capacity", 0),
            "performance_rating": contract.get("performance_rating", "unknown"),
            "violations_during_contract": contract.get("violations", 0),
            "deaths_during_contract": contract.get("deaths", 0),
        },
    )


def compute_cost_per_outcome(contractor_id: str, outcomes: dict) -> dict:
    """Compute cost per deportation, cost per detention-day. Emit outcome_receipt.

    Args:
        contractor_id: Contractor identifier
        outcomes: Outcome data (deportations, detentions, costs)

    Returns:
        outcome_receipt
    """
    total_cost = outcomes.get("total_cost", 0)
    deportations = outcomes.get("deportations", 0)
    detention_days = outcomes.get("detention_days", 0)

    cost_per_deportation = total_cost / deportations if deportations > 0 else 0
    cost_per_detention_day = total_cost / detention_days if detention_days > 0 else 0

    return emit_receipt(
        "contractor_outcome",
        {
            "tenant_id": TENANT_ID,
            "contractor_id": contractor_id,
            "total_cost": total_cost,
            "deportations": deportations,
            "detention_days": detention_days,
            "cost_per_deportation": cost_per_deportation,
            "cost_per_detention_day": cost_per_detention_day,
            "deaths": outcomes.get("deaths", 0),
            "cost_per_death": total_cost / outcomes["deaths"]
            if outcomes.get("deaths", 0) > 0
            else 0,
            "wrongful_detentions": outcomes.get("wrongful_detentions", 0),
        },
    )


def cross_reference_donations(contracts: list, donations: list) -> dict:
    """Cross-reference contracts with political donations. Emit donation_cross_ref_receipt.

    Args:
        contracts: List of contract records
        donations: List of donation records

    Returns:
        donation_cross_ref_receipt
    """
    # Build donation lookup by entity
    entity_donations = {}
    for d in donations:
        entity = d.get("donor", "").lower()
        if entity:
            if entity not in entity_donations:
                entity_donations[entity] = {
                    "total": 0,
                    "trump_related": 0,
                    "donations": [],
                }
            entity_donations[entity]["total"] += d.get("amount", 0)
            if "trump" in d.get("recipient", "").lower():
                entity_donations[entity]["trump_related"] += d.get("amount", 0)
            entity_donations[entity]["donations"].append(d)

    # Cross-reference with contracts
    correlations = []
    for contract in contracts:
        contractor = contract.get("contractor_name", "").lower()
        if contractor in entity_donations:
            correlations.append(
                {
                    "contractor": contractor,
                    "contract_value": contract.get("value", 0),
                    "total_donations": entity_donations[contractor]["total"],
                    "trump_related_donations": entity_donations[contractor][
                        "trump_related"
                    ],
                    "donation_to_contract_ratio": (
                        entity_donations[contractor]["total"] / contract.get("value", 1)
                        if contract.get("value", 0) > 0
                        else 0
                    ),
                }
            )

    total_contract_value = sum(c.get("contract_value", 0) for c in correlations)
    total_donations = sum(c.get("total_donations", 0) for c in correlations)

    return emit_receipt(
        "donation_contract_cross_ref",
        {
            "tenant_id": TENANT_ID,
            "contracts_analyzed": len(contracts),
            "donations_analyzed": len(donations),
            "correlations_found": len(correlations),
            "correlations": correlations,
            "total_correlated_contract_value": total_contract_value,
            "total_correlated_donations": total_donations,
            "corruption_risk": "high"
            if len(correlations) > 0 and total_donations > 1_000_000
            else "medium"
            if correlations
            else "low",
        },
    )
