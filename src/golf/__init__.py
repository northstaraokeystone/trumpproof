"""GolfProof Module

Foreign payment tracking, LIV Golf monitoring, emoluments compliance.
Operator: Eric Trump (Golf EVP)
Dollar Exposure: $354M annual golf revenue, $4.58B LIV Golf PIF investment

Key Data:
- LIV Golf 93% owned by Saudi PIF
- $7.8M minimum documented from 20+ foreign governments (first term)
- Up to $160M total estimated foreign payments
- 5+ LIV events at Trump properties
"""

from .payment import (
    register_payment,
    classify_source,
    aggregate_by_country,
)
from .event import (
    register_event,
    track_liv_event,
    compute_venue_revenue,
)
from .sanctions import (
    screen_entity,
    screen_transaction,
    flag_match,
)
from .emoluments import (
    assess_emolument,
    track_foreign_government,
    compute_exposure,
)

__all__ = [
    "register_payment",
    "classify_source",
    "aggregate_by_country",
    "register_event",
    "track_liv_event",
    "compute_venue_revenue",
    "screen_entity",
    "screen_transaction",
    "flag_match",
    "assess_emolument",
    "track_foreign_government",
    "compute_exposure",
]
