"""Tests for TrumpProof Core Module"""

import pytest
import json

from src.core import (
    dual_hash,
    emit_receipt,
    merkle,
    StopRule,
    TENANT_ID,
    stoprule_hash_mismatch,
    stoprule_unverified_claim,
)


class TestDualHash:
    """Tests for dual_hash function."""

    def test_dual_hash_returns_string(self):
        """dual_hash should return a string."""
        result = dual_hash("test")
        assert isinstance(result, str)

    def test_dual_hash_contains_colon(self):
        """dual_hash should return SHA256:BLAKE3 format."""
        result = dual_hash("test")
        assert ":" in result

    def test_dual_hash_bytes_input(self):
        """dual_hash should handle bytes input."""
        result = dual_hash(b"test")
        assert ":" in result

    def test_dual_hash_deterministic(self):
        """dual_hash should be deterministic."""
        h1 = dual_hash("trumpproof")
        h2 = dual_hash("trumpproof")
        assert h1 == h2

    def test_dual_hash_different_inputs(self):
        """dual_hash should produce different outputs for different inputs."""
        h1 = dual_hash("input1")
        h2 = dual_hash("input2")
        assert h1 != h2


class TestEmitReceipt:
    """Tests for emit_receipt function."""

    def test_emit_receipt_returns_dict(self, capture_receipts):
        """emit_receipt should return a dict."""
        result = emit_receipt("test", {"data": "value"})
        assert isinstance(result, dict)

    def test_emit_receipt_has_required_fields(self, capture_receipts):
        """emit_receipt should include required fields."""
        result = emit_receipt("test", {"tenant_id": TENANT_ID})
        assert "receipt_type" in result
        assert "ts" in result
        assert "tenant_id" in result
        assert "payload_hash" in result

    def test_emit_receipt_uses_correct_tenant(self, capture_receipts):
        """emit_receipt should use trumpproof tenant."""
        result = emit_receipt("test", {})
        assert result["tenant_id"] == "trumpproof"

    def test_emit_receipt_outputs_json(self, capture_receipts):
        """emit_receipt should output valid JSON to stdout."""
        emit_receipt("test", {"data": "value"})
        output = capture_receipts.getvalue()
        parsed = json.loads(output.strip())
        assert parsed["receipt_type"] == "test"


class TestMerkle:
    """Tests for merkle function."""

    def test_merkle_empty_list(self):
        """merkle should handle empty list."""
        result = merkle([])
        assert isinstance(result, str)
        assert ":" in result

    def test_merkle_single_item(self):
        """merkle should handle single item."""
        result = merkle([{"key": "value"}])
        assert isinstance(result, str)

    def test_merkle_multiple_items(self):
        """merkle should handle multiple items."""
        items = [{"a": 1}, {"b": 2}, {"c": 3}]
        result = merkle(items)
        assert isinstance(result, str)

    def test_merkle_deterministic(self):
        """merkle should be deterministic."""
        items = [{"a": 1}, {"b": 2}]
        m1 = merkle(items)
        m2 = merkle(items)
        assert m1 == m2


class TestStopRule:
    """Tests for StopRule exception."""

    def test_stoprule_is_exception(self):
        """StopRule should be an exception."""
        assert issubclass(StopRule, Exception)

    def test_stoprule_hash_mismatch(self, capture_receipts):
        """stoprule_hash_mismatch should raise StopRule."""
        with pytest.raises(StopRule):
            stoprule_hash_mismatch("expected", "actual")

    def test_stoprule_unverified_claim(self, capture_receipts):
        """stoprule_unverified_claim should raise StopRule."""
        with pytest.raises(StopRule):
            stoprule_unverified_claim({"type": "test"})


class TestTenantId:
    """Tests for TENANT_ID constant."""

    def test_tenant_id_is_trumpproof(self):
        """TENANT_ID should be 'trumpproof'."""
        assert TENANT_ID == "trumpproof"
