"""Tests for TrumpProof License Module"""

from src.license.ownership import (
    resolve_ownership,
    track_shell_company,
    flag_opacity,
)
from src.license.attestation import (
    register_license,
    track_fee_payment,
    verify_disclosure,
)
from src.license.partner import (
    register_partner,
    assess_government_ties,
    cross_reference_pif,
)


class TestLicenseOwnership:
    """Tests for license ownership functions."""

    def test_resolve_ownership(self, capture_receipts):
        """resolve_ownership should trace chain."""
        entity = {
            "name": "Trump Tower Jeddah LLC",
            "type": "llc",
            "parent_entity": {
                "name": "Trump Organization",
                "type": "corporation",
            },
        }
        result = resolve_ownership(entity)
        assert result["receipt_type"] == "ownership_resolution"
        assert len(result["ownership_chain"]) >= 1
        assert result["cta_exempt"]

    def test_track_shell_company(self, capture_receipts):
        """track_shell_company should identify indicators."""
        entity = {
            "name": "Delaware Holdings LLC",
            "no_employees": True,
            "registered_agent_only": True,
        }
        result = track_shell_company(entity, "Delaware")
        assert result["receipt_type"] == "shell_company"
        assert result["shell_score"] >= 0.4  # At least 2 indicators
        assert result["likely_shell"]

    def test_flag_opacity(self, capture_receipts):
        """flag_opacity should score unresolved layers."""
        result = flag_opacity("entity-001", unresolved_layers=4)
        assert result["receipt_type"] == "opacity_flag"
        assert result["opacity_score"] == 0.8
        assert result["severity"] == "critical"


class TestLicenseAttestation:
    """Tests for license attestation functions."""

    def test_register_license(self, capture_receipts):
        """register_license should emit receipt."""
        licensor = {"name": "Trump Organization"}
        licensee = {"name": "Dar Global", "country": "Saudi Arabia"}
        terms = {
            "project_name": "Trump Tower Jeddah",
            "project_value": 533_000_000,
            "fee_percentage": 5,
        }
        result = register_license(licensor, licensee, terms)
        assert result["receipt_type"] == "license_registration"
        assert result["project_value"] == 533_000_000

    def test_track_fee_payment(self, capture_receipts):
        """track_fee_payment should emit receipt."""
        payment = {
            "amount": 5_000_000,
            "date": "2024-06-01",
            "source": "Dar Global",
            "source_country": "Saudi Arabia",
            "is_foreign": True,
        }
        result = track_fee_payment("license-001", payment)
        assert result["receipt_type"] == "license_fee_payment"
        assert result["is_foreign"]

    def test_verify_disclosure_incomplete(self, capture_receipts):
        """verify_disclosure should detect missing fields."""
        disclosed = {
            "project_value": 533_000_000,
            "fee_percentage": 5,
            # Missing: licensee_beneficial_owner, source_of_funds, government_involvement
        }
        result = verify_disclosure("license-001", disclosed)
        assert result["receipt_type"] == "license_disclosure_verification"
        assert not result["adequate_disclosure"]
        assert len(result["missing_fields"]) == 3


class TestLicensePartner:
    """Tests for license partner functions."""

    def test_register_partner(self, capture_receipts):
        """register_partner should emit receipt."""
        partner = {
            "name": "Dar Global",
            "parent_company": "Dar Al Arkan",
            "projects": [{"name": "Trump Tower Jeddah", "value": 533_000_000}],
        }
        result = register_partner(partner, "Saudi Arabia")
        assert result["receipt_type"] == "partner_registration"
        assert result["total_project_value"] == 533_000_000

    def test_assess_government_ties(self, capture_receipts):
        """assess_government_ties should identify ties."""
        partner = {
            "name": "Dar Global",
            "country": "Saudi Arabia",
            "government_contracts": True,
            "government_contract_value": 100_000_000,
        }
        result = assess_government_ties("partner-001", partner)
        assert result["receipt_type"] == "government_ties"
        assert result["tie_count"] >= 1

    def test_cross_reference_pif(self, capture_receipts):
        """cross_reference_pif should identify PIF connection."""
        partner = {
            "name": "Dar Global",
            "parent_company": "Dar Al Arkan",
            "country": "Saudi Arabia",
        }
        result = cross_reference_pif(partner)
        assert result["receipt_type"] == "pif_cross_reference"
        assert result["is_pif_connected"]
