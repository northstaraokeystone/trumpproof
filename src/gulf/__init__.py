"""GulfProof Module

Sovereign wealth fund investment tracking, FARA compliance, return verification.
Operator: Jared Kushner (Affinity Partners)
Dollar Exposure: $2B from Saudi PIF, $5.4B AUM, $157M fees collected

Conflict Documentation:
- PIF screening panel voted AGAINST investment: "inexperience," "unsatisfactory operations"
- Crown Prince MBS personally overruled advisors
- Investment came 6 months after Kushner left White House
- Zero returns to investors
"""

from .investment import (
    register_swf_investment,
    track_deployment,
    verify_terms,
)
from .fara import (
    assess_fara_requirement,
    check_registration,
    flag_violation,
)
from .returns import (
    compute_returns,
    compare_to_benchmark,
    verify_reported_vs_actual,
)
from .fees import (
    track_fee,
    compute_fee_ratio,
    flag_excessive,
)

__all__ = [
    "register_swf_investment",
    "track_deployment",
    "verify_terms",
    "assess_fara_requirement",
    "check_registration",
    "flag_violation",
    "compute_returns",
    "compare_to_benchmark",
    "verify_reported_vs_actual",
    "track_fee",
    "compute_fee_ratio",
    "flag_excessive",
]
