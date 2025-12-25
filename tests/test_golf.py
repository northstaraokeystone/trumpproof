"""Tests for TrumpProof Golf Module"""

from src.golf.payment import (
    register_payment,
    classify_source,
    aggregate_by_country,
)
from src.golf.event import (
    register_event,
    track_liv_event,
    compute_venue_revenue,
)
from src.golf.sanctions import (
    screen_entity,
    screen_transaction,
    flag_match,
)
from src.golf.emoluments import (
    assess_emolument,
    track_foreign_government,
    compute_exposure,
)


class TestGolfPayment:
    """Tests for golf payment functions."""

    def test_register_payment(self, capture_receipts):
        """register_payment should emit receipt."""
        source = {"name": "Saudi Embassy", "country": "Saudi Arabia"}
        recipient = {"name": "Trump Hotel DC", "property": "Trump Hotel DC"}
        result = register_payment(source, recipient, 50_000)
        assert result["receipt_type"] == "payment"
        assert result["amount"] == 50_000

    def test_classify_source_foreign_government(self, capture_receipts):
        """classify_source should identify foreign government."""
        source = {
            "name": "Saudi Embassy",
            "country": "Saudi Arabia",
            "is_government": True,
        }
        result = classify_source(source)
        assert result["receipt_type"] == "source_classification"
        assert result["location_classification"] == "foreign"
        assert result["entity_type"] == "government"
        assert result["emoluments_concern"]

    def test_aggregate_by_country(self, capture_receipts):
        """aggregate_by_country should group payments."""
        payments = [
            {"source_country": "Saudi Arabia", "amount": 100_000},
            {"source_country": "Saudi Arabia", "amount": 50_000},
            {"source_country": "Qatar", "amount": 75_000},
        ]
        result = aggregate_by_country(payments)
        assert result["receipt_type"] == "country_aggregate"
        assert result["by_country"]["Saudi Arabia"]["total"] == 150_000


class TestGolfEvent:
    """Tests for golf event functions."""

    def test_register_event(self, capture_receipts):
        """register_event should emit receipt."""
        event = {"name": "LIV Golf Miami", "type": "LIV", "purse": 25_000_000}
        venue = {"name": "Trump Doral", "is_trump_property": True}
        result = register_event(event, venue)
        assert result["receipt_type"] == "golf_event"
        assert result["is_trump_property"]

    def test_track_liv_event(self, capture_receipts):
        """track_liv_event should track PIF funding."""
        event = {
            "name": "LIV Golf Team Championship",
            "venue": {"name": "Trump Doral", "is_trump_property": True},
            "purse": 50_000_000,
        }
        result = track_liv_event(event, pif_funding=46_500_000)
        assert result["receipt_type"] == "liv_event"
        assert result["pif_ownership_percentage"] == 93
        assert result["saudi_government_connection"]

    def test_compute_venue_revenue(self, capture_receipts):
        """compute_venue_revenue should compute LIV share."""
        events = [
            {"event_type": "LIV", "estimated_revenue": 5_000_000},
            {"event_type": "PGA", "estimated_revenue": 3_000_000},
        ]
        result = compute_venue_revenue("venue-001", "2024", events)
        assert result["receipt_type"] == "venue_revenue"
        assert result["liv_revenue"] == 5_000_000
        assert result["pif_exposure"] == 5_000_000 * 0.93


class TestGolfSanctions:
    """Tests for golf sanctions functions."""

    def test_screen_entity_clear(self, capture_receipts):
        """screen_entity should clear non-SDN entity."""
        entity = {"name": "Test Corp", "country": "USA"}
        result = screen_entity(entity, sdn_list=[])
        assert result["receipt_type"] == "sanctions_screening"
        assert result["cleared"]

    def test_screen_transaction(self, capture_receipts):
        """screen_transaction should screen both parties."""
        transaction = {
            "id": "txn-001",
            "sender": {"name": "Test Sender", "country": "USA"},
            "recipient": {"name": "Test Recipient", "country": "USA"},
            "amount": 100_000,
        }
        result = screen_transaction(transaction, sdn_list=[])
        assert result["receipt_type"] == "transaction_screening"
        assert not result["blocked"]

    def test_flag_match(self, capture_receipts):
        """flag_match should flag with severity."""
        sdn_match = {"sdn_id": "sdn-001", "confidence": 0.95}
        result = flag_match("entity-001", sdn_match)
        assert result["receipt_type"] == "sdn_flag"
        assert result["severity"] == "critical"


class TestGolfEmoluments:
    """Tests for golf emoluments functions."""

    def test_assess_emolument_positive(self, capture_receipts):
        """assess_emolument should identify emolument."""
        payment = {"id": "pay-001", "amount": 50_000}
        source = {
            "name": "Saudi Embassy",
            "country": "Saudi Arabia",
            "is_government": True,
        }
        result = assess_emolument(payment, source)
        assert result["receipt_type"] == "emolument_assessment"
        assert result["is_emolument"]

    def test_track_foreign_government(self, capture_receipts):
        """track_foreign_government should aggregate by country."""
        payments = [
            {"source_country": "Saudi Arabia", "amount": 100_000},
            {"source_country": "Saudi Arabia", "amount": 50_000},
        ]
        result = track_foreign_government(payments, "Saudi Arabia")
        assert result["receipt_type"] == "government_tracking"
        assert result["total_amount"] == 150_000

    def test_compute_exposure(self, capture_receipts):
        """compute_exposure should compute total emoluments."""
        payments = [
            {
                "amount": 100_000,
                "source": {"country": "Saudi Arabia", "is_government": True},
            },
            {"amount": 50_000, "source": {"country": "USA", "is_government": False}},
        ]
        result = compute_exposure(payments)
        assert result["receipt_type"] == "emoluments_exposure"
        assert result["emoluments_total"] == 100_000
