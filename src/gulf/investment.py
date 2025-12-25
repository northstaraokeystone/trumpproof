"""GulfProof Investment Module

Sovereign wealth fund registry and investment tracking.

Key Metrics:
- Only 33% capital deployed by July 2024
- $157M fees collected despite minimal deployment
- Another $90M guaranteed through Aug 2026

Receipts: swf_investment_receipt, deployment_receipt, terms_receipt
"""

from ..core import emit_receipt, dual_hash, TENANT_ID
from ..constants import GULF_PIF_INVESTMENT, GULF_AFFINITY_AUM


def register_swf_investment(fund: dict, recipient: dict, amount: float) -> dict:
    """Register sovereign wealth fund investment. Emit swf_investment_receipt.

    Args:
        fund: Sovereign wealth fund details
        recipient: Investment recipient details
        amount: Investment amount

    Returns:
        swf_investment_receipt
    """
    return emit_receipt("swf_investment", {
        "tenant_id": TENANT_ID,
        "fund_id": fund.get("id", dual_hash(str(fund))[:12]),
        "fund_name": fund.get("name", "unknown"),
        "fund_country": fund.get("country", "unknown"),
        "recipient_id": recipient.get("id", dual_hash(str(recipient))[:12]),
        "recipient_name": recipient.get("name", "unknown"),
        "amount": amount,
        "investment_date": fund.get("investment_date", "unknown"),
        "screening_panel_recommendation": fund.get("screening_recommendation", "unknown"),
        "override_by": fund.get("override_by", None),
        "pif_baseline": GULF_PIF_INVESTMENT,
    })


def track_deployment(investment_id: str, deployed: float, total: float) -> dict:
    """Track capital deployment rate. Emit deployment_receipt.

    Args:
        investment_id: Investment identifier
        deployed: Amount deployed
        total: Total commitment

    Returns:
        deployment_receipt
    """
    deployment_rate = deployed / total if total > 0 else 0

    # Flag low deployment (Affinity deployed only 33% by July 2024)
    low_deployment = deployment_rate < 0.5

    return emit_receipt("capital_deployment", {
        "tenant_id": TENANT_ID,
        "investment_id": investment_id,
        "deployed_amount": deployed,
        "total_commitment": total,
        "deployment_rate": deployment_rate,
        "deployment_percentage": deployment_rate * 100,
        "low_deployment_flag": low_deployment,
        "affinity_baseline_rate": 0.33,  # 33% deployed by July 2024
    })


def verify_terms(investment_id: str, terms: dict) -> dict:
    """Verify investment terms. Emit terms_receipt.

    Args:
        investment_id: Investment identifier
        terms: Documented terms

    Returns:
        terms_receipt
    """
    # Check for unusual terms
    unusual_flags = []

    # Management fee above market
    mgmt_fee = terms.get("management_fee_percentage", 0)
    if mgmt_fee > 2.0:
        unusual_flags.append({
            "type": "above_market_fee",
            "value": mgmt_fee,
            "market_standard": 2.0,
        })

    # Guaranteed fees regardless of performance
    if terms.get("guaranteed_fees", False):
        unusual_flags.append({
            "type": "guaranteed_fees",
            "guaranteed_amount": terms.get("guaranteed_amount", 0),
        })

    # No performance hurdle
    if not terms.get("performance_hurdle"):
        unusual_flags.append({
            "type": "no_performance_hurdle",
        })

    return emit_receipt("investment_terms", {
        "tenant_id": TENANT_ID,
        "investment_id": investment_id,
        "terms": terms,
        "unusual_flags": unusual_flags,
        "unusual_flag_count": len(unusual_flags),
        "risk_assessment": "high" if len(unusual_flags) >= 2 else "medium" if unusual_flags else "normal",
    })
