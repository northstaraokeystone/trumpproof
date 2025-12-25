"""Tests for TrumpProof Border Module"""

import pytest

from src.border.detention import (
    register_detainee,
    track_duration,
    monitor_facility,
    compute_cost_per_detainee,
)
from src.border.contractor import (
    register_contractor,
    track_contract,
    compute_cost_per_outcome,
    cross_reference_donations,
)
from src.border.citizenship import (
    verify_citizenship,
    flag_us_citizen,
    track_wrongful_detention,
)
from src.border.condition import (
    assess_conditions,
    track_violations,
    compute_death_rate,
)


class TestBorderDetention:
    """Tests for border detention functions."""

    def test_register_detainee(self, capture_receipts, sample_detainee):
        """register_detainee should emit receipt."""
        result = register_detainee(sample_detainee, "facility-001")
        assert result["receipt_type"] == "detention"
        assert result["tenant_id"] == "trumpproof"

    def test_track_duration(self, capture_receipts):
        """track_duration should compute days."""
        result = track_duration(
            "detainee-001",
            intake_date="2025-01-01T00:00:00Z",
            current_date="2025-01-15T00:00:00Z"
        )
        assert result["receipt_type"] == "detention_duration"
        assert result["duration_days"] == 14

    def test_monitor_facility(self, capture_receipts):
        """monitor_facility should emit receipt."""
        metrics = {
            "capacity": 500,
            "current_population": 450,
            "staffing_ratio": 0.1,
        }
        result = monitor_facility("facility-001", metrics)
        assert result["receipt_type"] == "facility_monitor"
        assert result["occupancy_rate"] == 0.9

    def test_compute_cost_per_detainee(self, capture_receipts):
        """compute_cost_per_detainee should compute costs."""
        result = compute_cost_per_detainee(
            "facility-001", "FY2025",
            total_cost=15_000_000,
            population=100,
            days=365
        )
        assert result["receipt_type"] == "detention_cost"
        # 15M / (100 * 365) ≈ $411/day
        assert result["cost_per_detainee_day"] > 400


class TestBorderContractor:
    """Tests for border contractor functions."""

    def test_register_contractor(self, capture_receipts):
        """register_contractor should emit receipt."""
        contractor = {
            "name": "Test Detention Inc",
            "type": "private",
            "donations": [{"amount": 100_000, "recipient": "Trump PAC"}]
        }
        result = register_contractor(contractor)
        assert result["receipt_type"] == "contractor_registration"
        assert result["trump_entity_donations"] == 100_000

    def test_compute_cost_per_outcome(self, capture_receipts):
        """compute_cost_per_outcome should compute metrics."""
        outcomes = {
            "total_cost": 100_000_000,
            "deportations": 1000,
            "detention_days": 500_000,
        }
        result = compute_cost_per_outcome("contractor-001", outcomes)
        assert result["receipt_type"] == "contractor_outcome"
        assert result["cost_per_deportation"] == 100_000


class TestBorderCitizenship:
    """Tests for border citizenship functions."""

    def test_verify_citizenship_strong_docs(self, capture_receipts):
        """verify_citizenship should rate strong docs."""
        documents = [
            {"type": "passport", "indicates_citizenship": True},
        ]
        result = verify_citizenship("detainee-001", documents)
        assert result["receipt_type"] == "citizenship_verification"
        assert result["verification_strength"] == "high"

    def test_flag_us_citizen(self, capture_receipts):
        """flag_us_citizen should emit critical flag."""
        evidence = {"type": "birth_certificate", "strength": "high"}
        result = flag_us_citizen("detainee-001", evidence)
        assert result["receipt_type"] == "citizen_flag"
        assert result["priority"] == "CRITICAL"

    def test_track_wrongful_detention(self, capture_receipts):
        """track_wrongful_detention should aggregate cases."""
        cases = [
            {"detention_days": 30, "resolved": True},
            {"detention_days": 60, "resolved": False},
        ]
        result = track_wrongful_detention(cases)
        assert result["receipt_type"] == "wrongful_detention_tracking"
        assert result["total_wrongful_detention_days"] == 90


class TestBorderCondition:
    """Tests for border condition functions."""

    def test_assess_conditions(self, capture_receipts):
        """assess_conditions should evaluate standards."""
        inspection = {
            "medical_care_adequate": True,
            "food_quality_adequate": True,
            "sanitation_adequate": False,
            "date": "2025-01-15",
        }
        result = assess_conditions("facility-001", inspection)
        assert result["receipt_type"] == "condition_assessment"

    def test_compute_death_rate(self, capture_receipts):
        """compute_death_rate should compute rate per 10K days."""
        result = compute_death_rate(
            "facility-001", "FY2025",
            deaths=2,
            detainee_days=100_000
        )
        assert result["receipt_type"] == "death_rate"
        # 2 deaths per 100K days = 0.2 per 10K days
        assert result["rate_per_10k_days"] == 0.2
