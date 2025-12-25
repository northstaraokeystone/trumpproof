"""LicenseProof Attestation Module

Licensing fee attestation.

Key Metrics:
- $36M annual foreign licensing revenue
- 23 Trump-branded projects in 11 countries

Receipts: license_receipt, fee_payment_receipt, disclosure_verification_receipt
"""

from ..core import emit_receipt, dual_hash, TENANT_ID
from ..constants import LICENSE_ANNUAL_REVENUE


def register_license(licensor: dict, licensee: dict, terms: dict) -> dict:
    """Register licensing agreement. Emit license_receipt.

    Args:
        licensor: Licensor entity (Trump Org)
        licensee: Licensee entity (developer)
        terms: License terms

    Returns:
        license_receipt
    """
    return emit_receipt("license_registration", {
        "tenant_id": TENANT_ID,
        "license_id": dual_hash(f"{licensor}{licensee}")[:16],
        "licensor_name": licensor.get("name", "unknown"),
        "licensee_name": licensee.get("name", "unknown"),
        "licensee_country": licensee.get("country", "unknown"),
        "project_name": terms.get("project_name", "unknown"),
        "project_value": terms.get("project_value", 0),
        "license_fee_percentage": terms.get("fee_percentage", 0),
        "estimated_annual_fee": terms.get("estimated_annual_fee", 0),
        "term_years": terms.get("term_years", 0),
        "start_date": terms.get("start_date", "unknown"),
    })


def track_fee_payment(license_id: str, payment: dict) -> dict:
    """Track fee payment. Emit fee_payment_receipt.

    Args:
        license_id: License identifier
        payment: Payment details

    Returns:
        fee_payment_receipt
    """
    return emit_receipt("license_fee_payment", {
        "tenant_id": TENANT_ID,
        "license_id": license_id,
        "payment_amount": payment.get("amount", 0),
        "payment_date": payment.get("date", "unknown"),
        "payment_method": payment.get("method", "unknown"),
        "source_entity": payment.get("source", "unknown"),
        "source_country": payment.get("source_country", "unknown"),
        "is_foreign": payment.get("is_foreign", False),
        "verified": payment.get("verified", False),
    })


def verify_disclosure(license_id: str, disclosed: dict) -> dict:
    """Verify disclosed vs actual terms. Emit disclosure_verification_receipt.

    Args:
        license_id: License identifier
        disclosed: Disclosed terms

    Returns:
        disclosure_verification_receipt
    """
    required_fields = [
        "project_value",
        "fee_percentage",
        "licensee_beneficial_owner",
        "source_of_funds",
        "government_involvement",
    ]

    disclosed_fields = []
    missing_fields = []

    for field in required_fields:
        if disclosed.get(field) is not None:
            disclosed_fields.append(field)
        else:
            missing_fields.append(field)

    disclosure_rate = len(disclosed_fields) / len(required_fields)
    adequate = disclosure_rate >= 0.8  # 80% disclosure threshold

    return emit_receipt("license_disclosure_verification", {
        "tenant_id": TENANT_ID,
        "license_id": license_id,
        "disclosed_fields": disclosed_fields,
        "missing_fields": missing_fields,
        "disclosure_rate": disclosure_rate,
        "adequate_disclosure": adequate,
        "annual_revenue_baseline": LICENSE_ANNUAL_REVENUE,
    })
