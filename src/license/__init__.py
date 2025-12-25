"""LicenseProof Module

Beneficial ownership tracking, licensing fee attestation, international partner monitoring.
Operator: Eric Trump (International)
Dollar Exposure: $36M annual foreign licensing revenue

Key Projects:
- 23 Trump-branded projects in 11 countries
- $533M Trump Tower Jeddah (Dec 2024)
- $1B Trump Plaza Jeddah (Sept 2025)
- $500M Trump International Oman (opens Dec 2028)

Infrastructure Gutted:
- Treasury March 2025 interim rule exempted ALL U.S. domestic entities from CTA
  beneficial ownership reporting
- Eliminated infrastructure requiring Trump Org to disclose beneficial ownership

LOW PRIORITY: CTA infrastructure destroyed, but track despite.
"""

from .ownership import (
    resolve_ownership,
    track_shell_company,
    flag_opacity,
)
from .attestation import (
    register_license,
    track_fee_payment,
    verify_disclosure,
)
from .partner import (
    register_partner,
    assess_government_ties,
    cross_reference_pif,
)

__all__ = [
    "resolve_ownership",
    "track_shell_company",
    "flag_opacity",
    "register_license",
    "track_fee_payment",
    "verify_disclosure",
    "register_partner",
    "assess_government_ties",
    "cross_reference_pif",
]
