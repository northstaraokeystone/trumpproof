"""TrumpProof Test Configuration"""

import pytest
import sys
import io


@pytest.fixture
def capture_receipts():
    """Fixture to capture receipt output."""
    old_stdout = sys.stdout
    sys.stdout = captured = io.StringIO()
    yield captured
    sys.stdout = old_stdout


@pytest.fixture
def sample_tariff_data():
    """Sample tariff data for testing."""
    return {
        "revenue_amount": 195_000_000_000,
        "period": "FY2025",
        "source": "cbp",
    }


@pytest.fixture
def sample_detainee():
    """Sample detainee data for testing."""
    return {
        "intake_date": "2025-01-15T10:00:00Z",
        "category": "test",
        "citizenship_verified": False,
    }


@pytest.fixture
def sample_swf_investment():
    """Sample SWF investment data for testing."""
    return {
        "fund": {
            "id": "pif-001",
            "name": "Saudi PIF",
            "country": "Saudi Arabia",
            "investment_date": "2022-06-01",
        },
        "recipient": {
            "id": "affinity-001",
            "name": "Affinity Partners",
        },
        "amount": 2_000_000_000,
    }
