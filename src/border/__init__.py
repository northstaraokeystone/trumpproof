"""BorderProof Module

Detention accountability, contractor cost tracking, citizenship verification, condition monitoring.
Operator: Tom Homan (Border Czar)
Dollar Exposure: $170.1B four-year allocation, $28.7B ICE FY2025

HIGHEST PRIORITY MODULE: Life-safety outcomes, constitutional verification.

Life-Safety Data:
- 2025 deadliest year for ICE custody since 2004
- 30-32 deaths documented (including 4 deaths in 4 days Dec 12-15)
- 170+ U.S. citizens wrongfully detained in first 9 months
"""

from .detention import (
    register_detainee,
    track_duration,
    monitor_facility,
    compute_cost_per_detainee,
)
from .contractor import (
    register_contractor,
    track_contract,
    compute_cost_per_outcome,
    cross_reference_donations,
)
from .citizenship import (
    verify_citizenship,
    flag_us_citizen,
    track_wrongful_detention,
)
from .condition import (
    assess_conditions,
    track_violations,
    compute_death_rate,
)

__all__ = [
    "register_detainee",
    "track_duration",
    "monitor_facility",
    "compute_cost_per_detainee",
    "register_contractor",
    "track_contract",
    "compute_cost_per_outcome",
    "cross_reference_donations",
    "verify_citizenship",
    "flag_us_citizen",
    "track_wrongful_detention",
    "assess_conditions",
    "track_violations",
    "compute_death_rate",
]
