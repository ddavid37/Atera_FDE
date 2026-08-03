"""Ticket analytics: Robin/Autopilot vs. technician resolution rate.

These functions operate only on plain ticket dictionaries as returned
by AteraClient.list_tickets / list_status_modified_tickets / get_ticket.
No requests import, no HTTP concerns - testable with fixture data alone.
"""

from datetime import date, datetime
from typing import Any, Optional


def is_robin_resolved(ticket: dict[str, Any]) -> bool:
    """Return True if a ticket appears to have been resolved by Robin/Autopilot.

    Working assumption: TechnicianContactID == -1 marks an Autopilot-owned
    ticket, inferred from the documented write-side behavior of
    POST /api/v3/tickets ("pass TechnicianContactID: -1" to assign to
    Autopilot). This has not yet been verified against live read data and
    is intentionally isolated here so it can be checked or swapped out.
    """
    return ticket.get("TechnicianContactID") == -1


def _parse_resolved_date(value: Any) -> Optional[date]:
    """Parse TicketResolvedDate into a date, or None if missing/unparseable."""
    if value is None or value == "":
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    # Accept full ISO timestamps or plain YYYY-MM-DD.
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            return None


def filter_by_window(tickets: list[dict[str, Any]], since: str, until: str) -> list[dict[str, Any]]:
    """Return tickets whose TicketResolvedDate falls within [since, until] (inclusive).

    Tickets with a missing or unparseable TicketResolvedDate are skipped.
    """
    start = date.fromisoformat(since)
    end = date.fromisoformat(until)
    if start > end:
        raise ValueError(f"since ({since}) must be on or before until ({until})")

    filtered: list[dict[str, Any]] = []
    for ticket in tickets:
        resolved = _parse_resolved_date(ticket.get("TicketResolvedDate"))
        if resolved is None:
            continue
        if start <= resolved <= end:
            filtered.append(ticket)
    return filtered


def filter_by_priority(
    tickets: list[dict[str, Any]], priority: str
) -> list[dict[str, Any]]:
    """Return tickets whose TicketPriority matches priority (case-insensitive).

    TicketPriority is not a query parameter on GET /api/v3/tickets, so this
    filter is applied client-side after the status-filtered fetch.
    """
    wanted = priority.strip().casefold()
    return [
        ticket
        for ticket in tickets
        if str(ticket.get("TicketPriority", "")).strip().casefold() == wanted
    ]


def compute_resolution_rate(tickets: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute Robin vs. technician resolution counts and rates for a set of tickets."""
    robin = sum(1 for ticket in tickets if is_robin_resolved(ticket))
    total = len(tickets)
    technician = total - robin
    return {
        "total": total,
        "robin": robin,
        "technician": technician,
        "robin_rate": (robin / total) if total else 0.0,
        "technician_rate": (technician / total) if total else 0.0,
    }
