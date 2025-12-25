"""TariffProof Module

Tariff revenue tracking, exemption transparency, refund liability verification.
Operator: Howard Lutnick (Commerce Secretary)
Dollar Exposure: $195B FY2025 revenue, $90B refund liability
"""

from .revenue import (
    ingest_customs_data,
    compute_allocation,
    verify_claimed_vs_actual,
    track_trend,
)
from .exemption import (
    register_exemption,
    track_approval,
    detect_favoritism,
    score_opacity,
)
from .refund import (
    compute_liability,
    track_claimant,
    model_scotus_outcomes,
)
from .lobby import (
    ingest_lda_filings,
    cross_reference,
    detect_pattern,
)

__all__ = [
    "ingest_customs_data",
    "compute_allocation",
    "verify_claimed_vs_actual",
    "track_trend",
    "register_exemption",
    "track_approval",
    "detect_favoritism",
    "score_opacity",
    "compute_liability",
    "track_claimant",
    "model_scotus_outcomes",
    "ingest_lda_filings",
    "cross_reference",
    "detect_pattern",
]
