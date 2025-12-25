"""GolfProof Event Module

Event verification and LIV Golf tracking.

Key Data:
- LIV Golf 93% owned by Saudi PIF ($4.58B invested through April 2025)
- 5+ LIV events at Trump properties (2022-2023)
- Team championship at Doral ($50M purse)

Receipts: event_receipt, liv_receipt, venue_revenue_receipt
"""

from ..core import emit_receipt, dual_hash, TENANT_ID
from ..constants import GOLF_LIV_PIF_INVESTMENT


def register_event(event: dict, venue: dict) -> dict:
    """Register golf event at venue. Emit event_receipt.

    Args:
        event: Event details
        venue: Venue details

    Returns:
        event_receipt
    """
    return emit_receipt(
        "golf_event",
        {
            "tenant_id": TENANT_ID,
            "event_id": event.get("id", dual_hash(str(event))[:12]),
            "event_name": event.get("name", "unknown"),
            "event_type": event.get("type", "unknown"),
            "event_date": event.get("date", "unknown"),
            "venue_id": venue.get("id", dual_hash(str(venue))[:12]),
            "venue_name": venue.get("name", "unknown"),
            "venue_owner": venue.get("owner", "unknown"),
            "is_trump_property": venue.get("is_trump_property", False),
            "purse_amount": event.get("purse", 0),
            "estimated_revenue": event.get("estimated_revenue", 0),
        },
    )


def track_liv_event(event: dict, pif_funding: float) -> dict:
    """Track LIV Golf event with PIF funding source. Emit liv_receipt.

    Args:
        event: LIV Golf event details
        pif_funding: Amount of Saudi PIF funding

    Returns:
        liv_receipt
    """
    venue = event.get("venue", {})
    is_trump = venue.get("is_trump_property", False)

    return emit_receipt(
        "liv_event",
        {
            "tenant_id": TENANT_ID,
            "event_id": event.get("id", dual_hash(str(event))[:12]),
            "event_name": event.get("name", "unknown"),
            "event_date": event.get("date", "unknown"),
            "venue_name": venue.get("name", "unknown"),
            "is_trump_property": is_trump,
            "pif_funding": pif_funding,
            "pif_ownership_percentage": 93,  # LIV Golf 93% PIF-owned
            "purse_amount": event.get("purse", 0),
            "pif_portion_of_purse": event.get("purse", 0) * 0.93,
            "total_pif_investment": GOLF_LIV_PIF_INVESTMENT,
            "saudi_government_connection": True,
        },
    )


def compute_venue_revenue(venue_id: str, period: str, events: list = None) -> dict:
    """Compute venue revenue from events. Emit venue_revenue_receipt.

    Args:
        venue_id: Venue identifier
        period: Reporting period
        events: List of events at venue

    Returns:
        venue_revenue_receipt
    """
    events = events or []

    total_revenue = sum(e.get("estimated_revenue", 0) for e in events)
    liv_events = [e for e in events if e.get("event_type", "").lower() == "liv"]
    liv_revenue = sum(e.get("estimated_revenue", 0) for e in liv_events)

    pga_events = [e for e in events if e.get("event_type", "").lower() == "pga"]
    pga_revenue = sum(e.get("estimated_revenue", 0) for e in pga_events)

    return emit_receipt(
        "venue_revenue",
        {
            "tenant_id": TENANT_ID,
            "venue_id": venue_id,
            "period": period,
            "total_events": len(events),
            "total_revenue": total_revenue,
            "liv_events": len(liv_events),
            "liv_revenue": liv_revenue,
            "liv_revenue_percentage": (liv_revenue / total_revenue * 100)
            if total_revenue > 0
            else 0,
            "pga_events": len(pga_events),
            "pga_revenue": pga_revenue,
            "other_events": len(events) - len(liv_events) - len(pga_events),
            "pif_exposure": liv_revenue * 0.93,  # 93% PIF-owned
        },
    )
