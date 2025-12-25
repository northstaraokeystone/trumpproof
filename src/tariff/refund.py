"""TariffProof Refund Module

Track $90B refund liability exposure.
Supreme Court IEEPA case: oral arguments Nov 5, 2025; decision expected early 2026.

Conflict Documentation:
- Lutnick sold Cantor Fitzgerald stake to sons for $360M
- Family firm allegedly created "litigation finance" product buying tariff refund rights
  at 20-30 cents/dollar
- Senate investigation by Wyden/Warren (Aug 2025)

Receipts: liability_receipt, claimant_receipt, scenario_receipt
"""

from ..core import emit_receipt, TENANT_ID
from ..constants import TARIFF_REFUND_LIABILITY


def compute_liability(tariff_data: list, ieepa_status: str = "pending") -> dict:
    """Compute refund liability by scenario. Emit liability_receipt.

    Args:
        tariff_data: List of tariff collection records
        ieepa_status: Status of IEEPA authority ("pending", "affirmed", "struck")

    Returns:
        liability_receipt with exposure by scenario
    """
    total_collected = sum(t.get("amount", 0) for t in tariff_data)

    # Scenario modeling
    scenarios = {
        "affirmed": {
            "description": "Supreme Court affirms IEEPA authority",
            "refund_liability": 0,
            "exposure_percentage": 0,
        },
        "struck_partial": {
            "description": "IEEPA struck for specific tariffs only",
            "refund_liability": total_collected * 0.3,  # 30% exposure
            "exposure_percentage": 30,
        },
        "struck_full": {
            "description": "IEEPA authority fully invalidated",
            "refund_liability": total_collected,
            "exposure_percentage": 100,
        }
    }

    current_scenario = scenarios.get(ieepa_status, scenarios["affirmed"])

    return emit_receipt("refund_liability", {
        "tenant_id": TENANT_ID,
        "total_collected": total_collected,
        "ieepa_status": ieepa_status,
        "baseline_liability": TARIFF_REFUND_LIABILITY,
        "scenarios": scenarios,
        "current_scenario": current_scenario,
        "scotus_oral_args": "2025-11-05",
        "decision_expected": "2026-Q1",
    })


def track_claimant(claimant: dict, amount: float) -> dict:
    """Track refund claimant. Emit claimant_receipt.

    Args:
        claimant: Claimant entity details
        amount: Claimed refund amount

    Returns:
        claimant_receipt
    """
    # Flag if claimant appears to be litigation finance
    is_litigation_finance = (
        "litigation" in claimant.get("type", "").lower() or
        "finance" in claimant.get("type", "").lower() or
        claimant.get("purchased_rights", False)
    )

    return emit_receipt("refund_claimant", {
        "tenant_id": TENANT_ID,
        "claimant_name": claimant.get("name", "unknown"),
        "claimant_type": claimant.get("type", "unknown"),
        "claim_amount": amount,
        "is_litigation_finance": is_litigation_finance,
        "purchased_rights": claimant.get("purchased_rights", False),
        "purchase_price": claimant.get("purchase_price", 0),
        "discount_rate": claimant.get("discount_rate", 0),  # e.g., 0.25 = 25 cents/dollar
    })


def model_scotus_outcomes(scenarios: list) -> dict:
    """Model outcomes by Supreme Court decision. Emit scenario_receipt.

    Args:
        scenarios: List of scenario configurations

    Returns:
        scenario_receipt with probability-weighted analysis
    """
    results = []

    for scenario in scenarios:
        name = scenario.get("name", "unknown")
        probability = scenario.get("probability", 0)
        refund_pct = scenario.get("refund_percentage", 0)

        liability = TARIFF_REFUND_LIABILITY * (refund_pct / 100)
        weighted_liability = liability * probability

        results.append({
            "scenario": name,
            "probability": probability,
            "refund_percentage": refund_pct,
            "raw_liability": liability,
            "weighted_liability": weighted_liability,
        })

    expected_liability = sum(r["weighted_liability"] for r in results)

    return emit_receipt("scotus_scenario", {
        "tenant_id": TENANT_ID,
        "scenarios": results,
        "expected_liability": expected_liability,
        "baseline_liability": TARIFF_REFUND_LIABILITY,
        "expected_pct_of_baseline": (expected_liability / TARIFF_REFUND_LIABILITY * 100)
            if TARIFF_REFUND_LIABILITY else 0,
    })
