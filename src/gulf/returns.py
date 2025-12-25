"""GulfProof Returns Module

Investment return verification.

Key Metrics:
- Affinity Partners: $157M fees collected on zero returns
- $87M from Saudi PIF alone
- Another $90M guaranteed through Aug 2026

Receipts: returns_receipt, benchmark_receipt, verification_receipt
"""

from ..core import emit_receipt, TENANT_ID
from ..constants import GULF_FEES_COLLECTED


def compute_returns(investment_id: str, period: str,
                    initial_value: float = 0, current_value: float = 0,
                    distributions: float = 0) -> dict:
    """Compute investment returns. Emit returns_receipt.

    Args:
        investment_id: Investment identifier
        period: Reporting period
        initial_value: Initial investment value
        current_value: Current portfolio value
        distributions: Cash distributions to investors

    Returns:
        returns_receipt
    """
    total_value = current_value + distributions

    if initial_value > 0:
        total_return = (total_value - initial_value) / initial_value
        return_percentage = total_return * 100
    else:
        total_return = 0
        return_percentage = 0

    return emit_receipt("investment_returns", {
        "tenant_id": TENANT_ID,
        "investment_id": investment_id,
        "period": period,
        "initial_value": initial_value,
        "current_value": current_value,
        "distributions": distributions,
        "total_value": total_value,
        "total_return": total_return,
        "return_percentage": return_percentage,
        "is_zero_return": return_percentage == 0 and initial_value > 0,
    })


def compare_to_benchmark(returns: dict, benchmark: str,
                         benchmark_return: float = 0) -> dict:
    """Compare to market benchmark. Emit benchmark_receipt.

    Args:
        returns: Returns data from compute_returns
        benchmark: Benchmark name (e.g., "S&P 500", "MSCI World")
        benchmark_return: Benchmark return percentage

    Returns:
        benchmark_receipt
    """
    fund_return = returns.get("return_percentage", 0)
    alpha = fund_return - benchmark_return

    underperformance = alpha < 0
    significant_underperformance = alpha < -10  # 10+ percentage points below benchmark

    return emit_receipt("benchmark_comparison", {
        "tenant_id": TENANT_ID,
        "investment_id": returns.get("investment_id", "unknown"),
        "fund_return_percentage": fund_return,
        "benchmark": benchmark,
        "benchmark_return_percentage": benchmark_return,
        "alpha": alpha,
        "underperformance": underperformance,
        "significant_underperformance": significant_underperformance,
    })


def verify_reported_vs_actual(reported: dict, actual: dict) -> dict:
    """Verify reported vs actual returns. Emit verification_receipt.

    Args:
        reported: Reported return figures
        actual: Verified actual figures

    Returns:
        verification_receipt
    """
    discrepancies = {}

    for key in reported:
        if key in actual:
            reported_val = reported[key]
            actual_val = actual[key]
            if abs(reported_val - actual_val) > 0.01:  # 1% tolerance
                discrepancies[key] = {
                    "reported": reported_val,
                    "actual": actual_val,
                    "difference": reported_val - actual_val,
                    "percentage_difference": (
                        (reported_val - actual_val) / actual_val * 100
                        if actual_val != 0 else float('inf')
                    ),
                }

    match = len(discrepancies) == 0

    return emit_receipt("returns_verification", {
        "tenant_id": TENANT_ID,
        "reported": reported,
        "actual": actual,
        "discrepancies": discrepancies,
        "match": match,
        "discrepancy_count": len(discrepancies),
        "fees_collected_baseline": GULF_FEES_COLLECTED,
    })
