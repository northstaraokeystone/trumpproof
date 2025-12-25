"""Loop Module

Cross-domain pattern detection, Saudi PIF central node monitoring,
self-improvement with human oversight.

60-second SENSE→ACTUATE cycle per ProofPack v3 specification.
"""

from .cycle import (
    run_cycle,
    sense,
    analyze,
    emit_cycle_receipt,
)
from .harvest import (
    harvest_violations,
    rank_by_exposure,
    propose_remediation,
)
from .cross_domain import (
    detect_entity_overlap,
    trace_money_flow,
    compute_centrality,
    flag_pif_connection,
)
from .pif_tracker import (
    track_pif_entity,
    aggregate_pif_exposure,
    detect_pif_pattern,
)

__all__ = [
    "run_cycle",
    "sense",
    "analyze",
    "emit_cycle_receipt",
    "harvest_violations",
    "rank_by_exposure",
    "propose_remediation",
    "detect_entity_overlap",
    "trace_money_flow",
    "compute_centrality",
    "flag_pif_connection",
    "track_pif_entity",
    "aggregate_pif_exposure",
    "detect_pif_pattern",
]
