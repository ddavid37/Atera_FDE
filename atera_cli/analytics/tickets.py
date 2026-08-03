"""Ticket analytics: Robin/Autopilot vs. technician resolution rate.

These functions operate only on plain ticket dictionaries as returned
by AteraClient.list_tickets / list_status_modified_tickets / get_ticket.
No requests import, no HTTP concerns - testable with fixture data alone.
"""

from typing import Any


def is_robin_resolved(ticket: dict[str, Any]) -> bool:
    """Return True if a ticket appears to have been resolved by Robin/Autopilot.

    Working assumption: TechnicianContactID == -1 marks an Autopilot-owned
    ticket, inferred from the documented write-side behavior of
    POST /api/v3/tickets ("pass TechnicianContactID: -1" to assign to
    Autopilot). This has not yet been verified against live read data and
    is intentionally isolated here so it can be checked or swapped out.
    """
    raise NotImplementedError


def filter_by_window(tickets: list[dict[str, Any]], since: str, until: str) -> list[dict[str, Any]]:
    """Return tickets whose TicketResolvedDate falls within [since, until]."""
    raise NotImplementedError


def compute_resolution_rate(tickets: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute Robin vs. technician resolution counts and rates for a set of tickets."""
    raise NotImplementedError
