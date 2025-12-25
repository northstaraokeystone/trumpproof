"""Tests for TrumpProof Tariff Module"""

import pytest

from src.tariff.revenue import (
    ingest_customs_data,
    compute_allocation,
    verify_claimed_vs_actual,
    track_trend,
)
from src.tariff.exemption import (
    register_exemption,
    track_approval,
    detect_favoritism,
    score_opacity,
)
from src.tariff.refund import (
    compute_liability,
    track_claimant,
    model_scotus_outcomes,
)
from src.tariff.lobby import (
    ingest_lda_filings,
    cross_reference,
    detect_pattern,
)


class TestTariffRevenue:
    """Tests for tariff revenue functions."""

    def test_ingest_customs_data(self, capture_receipts, sample_tariff_data):
        """ingest_customs_data should emit receipt."""
        result = ingest_customs_data(sample_tariff_data)
        assert result["receipt_type"] == "tariff_ingest"
        assert result["tenant_id"] == "trumpproof"

    def test_compute_allocation(self, capture_receipts):
        """compute_allocation should compute correct allocations."""
        categories = [
            {"name": "general", "percentage": 60},
            {"name": "defense", "percentage": 40},
        ]
        result = compute_allocation(100_000_000, categories)
        assert result["receipt_type"] == "tariff_allocation"
        assert result["allocations"]["general"] == 60_000_000
        assert result["allocations"]["defense"] == 40_000_000

    def test_verify_claimed_vs_actual_match(self, capture_receipts):
        """verify_claimed_vs_actual should detect match."""
        claimed = {"revenue": 100}
        actual = {"revenue": 100}
        result = verify_claimed_vs_actual(claimed, actual)
        assert result["match_status"] == "verified"

    def test_verify_claimed_vs_actual_discrepancy(self, capture_receipts):
        """verify_claimed_vs_actual should detect discrepancy."""
        claimed = {"revenue": 150}
        actual = {"revenue": 100}
        result = verify_claimed_vs_actual(claimed, actual)
        assert result["match_status"] == "discrepancy_detected"


class TestTariffExemption:
    """Tests for tariff exemption functions."""

    def test_register_exemption(self, capture_receipts):
        """register_exemption should emit receipt."""
        application = {
            "applicant": "Test Corp",
            "product": "Steel",
            "amount_requested": 1_000_000,
        }
        result = register_exemption(application)
        assert result["receipt_type"] == "exemption_application"

    def test_track_approval(self, capture_receipts):
        """track_approval should emit receipt."""
        result = track_approval("ex-001", "approved", "Met criteria")
        assert result["receipt_type"] == "exemption_outcome"
        assert result["outcome"] == "approved"

    def test_detect_favoritism_no_lobbying(self, capture_receipts):
        """detect_favoritism should work with no lobbying data."""
        outcomes = [
            {"applicant": "Corp A", "outcome": "approved"},
            {"applicant": "Corp B", "outcome": "denied"},
        ]
        result = detect_favoritism(outcomes, [])
        assert result["receipt_type"] == "favoritism_detection"

    def test_score_opacity_empty(self, capture_receipts):
        """score_opacity should handle empty list."""
        result = score_opacity([])
        assert result["opacity_score"] == 1.0


class TestTariffRefund:
    """Tests for tariff refund functions."""

    def test_compute_liability(self, capture_receipts):
        """compute_liability should compute refund exposure."""
        tariff_data = [{"amount": 100_000_000}]
        result = compute_liability(tariff_data, "pending")
        assert result["receipt_type"] == "refund_liability"

    def test_track_claimant(self, capture_receipts):
        """track_claimant should emit receipt."""
        claimant = {"name": "Test LLC", "type": "importer"}
        result = track_claimant(claimant, 50_000_000)
        assert result["receipt_type"] == "refund_claimant"

    def test_model_scotus_outcomes(self, capture_receipts):
        """model_scotus_outcomes should model scenarios."""
        scenarios = [
            {"name": "affirmed", "probability": 0.6, "refund_percentage": 0},
            {"name": "struck", "probability": 0.4, "refund_percentage": 100},
        ]
        result = model_scotus_outcomes(scenarios)
        assert result["receipt_type"] == "scotus_scenario"


class TestTariffLobby:
    """Tests for tariff lobby functions."""

    def test_ingest_lda_filings(self, capture_receipts):
        """ingest_lda_filings should emit receipt."""
        filings = [
            {"client": "Corp A", "lobbyist": "Lobbyist 1", "amount": 100_000},
        ]
        result = ingest_lda_filings(filings)
        assert result["receipt_type"] == "lda_ingest"

    def test_cross_reference(self, capture_receipts):
        """cross_reference should find matches."""
        exemptions = [{"applicant": "Corp A", "outcome": "approved"}]
        filings = [{"client": "Corp A", "lobbyist": "Lobbyist 1"}]
        result = cross_reference(exemptions, filings)
        assert result["receipt_type"] == "exemption_lobbying_cross_ref"
        assert result["matches_found"] == 1
