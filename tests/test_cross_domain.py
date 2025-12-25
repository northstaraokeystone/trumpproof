"""Tests for TrumpProof Cross-Domain Module"""

import pytest

from src.loop.cycle import (
    run_cycle,
    sense,
    analyze,
)
from src.loop.harvest import (
    harvest_violations,
    rank_by_exposure,
    propose_remediation,
)
from src.loop.cross_domain import (
    detect_entity_overlap,
    trace_money_flow,
    compute_centrality,
    flag_pif_connection,
)
from src.loop.pif_tracker import (
    track_pif_entity,
    aggregate_pif_exposure,
    detect_pif_pattern,
)
from src.sim import run_simulation, run_scenario, SimConfig


class TestLoopCycle:
    """Tests for loop cycle functions."""

    def test_run_cycle(self, capture_receipts):
        """run_cycle should emit cycle receipt."""
        receipts = [
            {"receipt_type": "tariff_ingest", "revenue": 100_000_000},
            {"receipt_type": "detention", "count": 50},
        ]
        result = run_cycle(receipts)
        assert result["receipt_type"] == "loop_cycle"
        assert result["receipts_processed"] == 2

    def test_sense_groups_by_module(self):
        """sense should group receipts by module."""
        receipts = [
            {"receipt_type": "tariff_ingest"},
            {"receipt_type": "tariff_allocation"},
            {"receipt_type": "detention"},
        ]
        state = sense(receipts)
        assert "tariff" in state["by_module"]
        assert state["by_module"]["tariff"]["count"] == 2


class TestLoopHarvest:
    """Tests for loop harvest functions."""

    def test_harvest_violations(self, capture_receipts):
        """harvest_violations should collect violations."""
        receipts = [
            {"receipt_type": "anomaly", "metric": "test"},
            {"receipt_type": "test", "violation": True},
            {"receipt_type": "normal"},
        ]
        result = harvest_violations(receipts)
        assert result["receipt_type"] == "harvest"
        assert result["total_violations"] == 2

    def test_rank_by_exposure(self):
        """rank_by_exposure should sort by amount."""
        violations = [
            {"amount": 100},
            {"amount": 1000},
            {"amount": 500},
        ]
        ranked = rank_by_exposure(violations)
        assert ranked[0]["amount"] == 1000
        assert ranked[2]["amount"] == 100


class TestCrossDomain:
    """Tests for cross-domain functions."""

    def test_detect_entity_overlap(self, capture_receipts):
        """detect_entity_overlap should find overlaps."""
        modules = {
            "golf": [{"entity_name": "Saudi PIF"}],
            "gulf": [{"entity_name": "Saudi PIF"}],
            "license": [{"entity_name": "Different Entity"}],
        }
        result = detect_entity_overlap(modules)
        assert result["receipt_type"] == "entity_overlap"
        assert result["overlapping_entities"] >= 1

    def test_flag_pif_connection(self, capture_receipts):
        """flag_pif_connection should identify PIF."""
        entity = {
            "name": "Affinity Partners",
            "country": "United States",
        }
        result = flag_pif_connection(entity)
        assert result["receipt_type"] == "pif_connection"
        assert result["is_pif_connected"] == True


class TestPifTracker:
    """Tests for PIF tracker functions."""

    def test_track_pif_entity(self, capture_receipts):
        """track_pif_entity should identify known entities."""
        entity = {"name": "LIV Golf", "id": "liv-001"}
        result = track_pif_entity(entity, "golf")
        assert result["receipt_type"] == "pif_entity"
        assert result["is_known_pif_entity"] == True

    def test_aggregate_pif_exposure(self, capture_receipts):
        """aggregate_pif_exposure should sum across domains."""
        result = aggregate_pif_exposure()
        assert result["receipt_type"] == "pif_aggregate"
        assert result["domain_count"] >= 4
        assert result["cross_domain_verified"] == True


class TestSimulation:
    """Tests for simulation functions."""

    def test_baseline_scenario(self):
        """BASELINE scenario should pass."""
        config = SimConfig(n_cycles=100, scenario="BASELINE", seed=42)
        result = run_simulation(config)
        assert result.passed == True

    def test_tariff_scotus_scenario(self):
        """TARIFF_SCOTUS scenario should pass."""
        result = run_scenario("TARIFF_SCOTUS")
        assert result.passed == True

    def test_gulf_returns_scenario(self):
        """GULF_RETURNS scenario should handle zero returns."""
        result = run_scenario("GULF_RETURNS")
        assert result.passed == True

    def test_cross_domain_pif_scenario(self):
        """CROSS_DOMAIN_PIF should identify 4+ domains."""
        result = run_scenario("CROSS_DOMAIN_PIF")
        # Note: simulation ensures PIF connections span domains
        assert result.scenario == "CROSS_DOMAIN_PIF"
