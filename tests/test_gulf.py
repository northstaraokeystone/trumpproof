"""Tests for TrumpProof Gulf Module"""

import pytest

from src.gulf.investment import (
    register_swf_investment,
    track_deployment,
    verify_terms,
)
from src.gulf.fara import (
    assess_fara_requirement,
    check_registration,
    flag_violation,
)
from src.gulf.returns import (
    compute_returns,
    compare_to_benchmark,
    verify_reported_vs_actual,
)
from src.gulf.fees import (
    track_fee,
    compute_fee_ratio,
    flag_excessive,
)


class TestGulfInvestment:
    """Tests for gulf investment functions."""

    def test_register_swf_investment(self, capture_receipts, sample_swf_investment):
        """register_swf_investment should emit receipt."""
        result = register_swf_investment(
            sample_swf_investment["fund"],
            sample_swf_investment["recipient"],
            sample_swf_investment["amount"]
        )
        assert result["receipt_type"] == "swf_investment"
        assert result["amount"] == 2_000_000_000

    def test_track_deployment(self, capture_receipts):
        """track_deployment should compute rate."""
        result = track_deployment("inv-001", deployed=660_000_000, total=2_000_000_000)
        assert result["receipt_type"] == "capital_deployment"
        assert result["deployment_rate"] == 0.33

    def test_verify_terms_unusual(self, capture_receipts):
        """verify_terms should flag unusual terms."""
        terms = {
            "management_fee_percentage": 3.0,  # Above market
            "guaranteed_fees": True,
            "guaranteed_amount": 90_000_000,
        }
        result = verify_terms("inv-001", terms)
        assert result["receipt_type"] == "investment_terms"
        assert len(result["unusual_flags"]) >= 2


class TestGulfFara:
    """Tests for gulf FARA functions."""

    def test_assess_fara_requirement(self, capture_receipts):
        """assess_fara_requirement should assess registration need."""
        entity = {
            "name": "Test Entity",
            "political_activities": True,
        }
        payments = [
            {"amount": 50_000_000, "source": "Saudi PIF", "is_government": True}
        ]
        result = assess_fara_requirement(entity, payments)
        assert result["receipt_type"] == "fara_assessment"
        assert result["requires_registration"] == True

    def test_check_registration(self, capture_receipts):
        """check_registration should check DOJ database."""
        result = check_registration("entity-001", registered=False)
        assert result["receipt_type"] == "fara_check"
        assert result["is_registered"] == False

    def test_flag_violation(self, capture_receipts):
        """flag_violation should flag with severity."""
        evidence = {"government_payments": 50_000_000}
        result = flag_violation("entity-001", evidence)
        assert result["receipt_type"] == "fara_violation"
        assert result["severity"] == "critical"


class TestGulfReturns:
    """Tests for gulf returns functions."""

    def test_compute_returns_zero(self, capture_receipts):
        """compute_returns should handle zero returns."""
        result = compute_returns(
            "inv-001", "FY2024",
            initial_value=2_000_000_000,
            current_value=2_000_000_000,
            distributions=0
        )
        assert result["receipt_type"] == "investment_returns"
        assert result["return_percentage"] == 0
        assert result["is_zero_return"] == True

    def test_compare_to_benchmark(self, capture_receipts):
        """compare_to_benchmark should compute alpha."""
        returns = {"investment_id": "inv-001", "return_percentage": 0}
        result = compare_to_benchmark(returns, "S&P 500", benchmark_return=10.0)
        assert result["receipt_type"] == "benchmark_comparison"
        assert result["alpha"] == -10.0
        assert result["significant_underperformance"] == True


class TestGulfFees:
    """Tests for gulf fees functions."""

    def test_track_fee(self, capture_receipts):
        """track_fee should emit receipt."""
        fee = {
            "type": "management",
            "amount": 50_000_000,
            "period": "FY2024",
            "source": "Saudi PIF",
            "aum": 2_000_000_000,
        }
        result = track_fee("fund-001", fee)
        assert result["receipt_type"] == "management_fee"
        assert result["fee_percentage"] == 2.5

    def test_compute_fee_ratio_zero_returns(self, capture_receipts):
        """compute_fee_ratio should handle zero returns (infinity)."""
        result = compute_fee_ratio(fees=157_000_000, returns=0)
        assert result["receipt_type"] == "fee_ratio"
        assert result["ratio"] == "infinity"
        assert result["excessive"] == True

    def test_flag_excessive(self, capture_receipts):
        """flag_excessive should flag high ratios."""
        result = flag_excessive(ratio=float('inf'))
        assert result["receipt_type"] == "excessive_fee_flag"
        assert result["severity"] == "critical"
