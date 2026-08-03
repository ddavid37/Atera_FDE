"""Command-line interface for the Atera CLI toolkit.

This is the composition root: the only module that wires together
AteraClient (HTTP) and analytics functions (pure). It parses
arguments, dispatches to a command handler, and formats/prints output.
"""

import argparse
import json
import sys
from typing import Any, Optional, Sequence

from atera_cli.analytics.tickets import (
    compute_resolution_rate,
    filter_by_priority,
    filter_by_window,
)
from atera_cli.client import AteraClient
from atera_cli.exceptions import AteraError


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser and its subcommands."""
    parser = argparse.ArgumentParser(
        prog="atera_cli",
        description="Command-line tools for the Atera Public API.",
    )
    subparsers = parser.add_subparsers(dest="command")

    tickets_parser = subparsers.add_parser("tickets", help="Ticket-related commands")
    tickets_subparsers = tickets_parser.add_subparsers(dest="tickets_command")

    list_parser = tickets_subparsers.add_parser(
        "list",
        help="List tickets filtered by status (API) and optionally priority (client-side)",
    )
    list_parser.add_argument(
        "--status",
        default="Open",
        help="Ticket status passed to the API ticketStatus filter (default: Open)",
    )
    list_parser.add_argument(
        "--priority",
        default="Critical",
        help="Client-side TicketPriority filter (default: Critical)",
    )
    list_parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )

    get_parser = tickets_subparsers.add_parser(
        "get",
        help="Fetch a single ticket by TicketID",
    )
    get_parser.add_argument(
        "ticket_id",
        type=int,
        help="Ticket ID (e.g. 912)",
    )
    get_parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )

    resolution_rate_parser = tickets_subparsers.add_parser(
        "resolution-rate",
        help="Compute the Robin vs. technician ticket resolution rate over a time window",
    )
    resolution_rate_parser.add_argument(
        "--since",
        required=True,
        help="Window start date (YYYY-MM-DD), inclusive",
    )
    resolution_rate_parser.add_argument(
        "--until",
        required=True,
        help="Window end date (YYYY-MM-DD), inclusive",
    )
    resolution_rate_parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )

    return parser


def _format_rate(value: float) -> str:
    return f"{value * 100:.1f}%"


def _print_resolution_rate(metrics: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(metrics, indent=2))
        return

    print("Ticket resolution rate")
    print(f"  Total resolved:     {metrics['total']}")
    print(f"  Robin/Autopilot:    {metrics['robin']} ({_format_rate(metrics['robin_rate'])})")
    print(f"  Technician:         {metrics['technician']} ({_format_rate(metrics['technician_rate'])})")


def _ticket_row(ticket: dict[str, Any]) -> dict[str, Any]:
    return {
        "TicketID": ticket.get("TicketID"),
        "TicketTitle": ticket.get("TicketTitle"),
        "CustomerName": ticket.get("CustomerName"),
        "TechnicianFullName": ticket.get("TechnicianFullName"),
        "TicketPriority": ticket.get("TicketPriority"),
        "TicketStatus": ticket.get("TicketStatus"),
    }


def _print_ticket_list(tickets: list[dict[str, Any]], output_format: str) -> None:
    rows = [_ticket_row(ticket) for ticket in tickets]
    if output_format == "json":
        print(json.dumps(rows, indent=2))
        return

    print(f"Tickets ({len(rows)})")
    if not rows:
        print("  (none)")
        return

    for row in rows:
        ticket_id = row["TicketID"]
        title = row["TicketTitle"] or ""
        customer = row["CustomerName"] or "-"
        tech = row["TechnicianFullName"] or "Unassigned"
        priority = row["TicketPriority"] or "-"
        status = row["TicketStatus"] or "-"
        print(f"  #{ticket_id}  [{priority}/{status}]  {title}")
        print(f"           customer={customer}  technician={tech}")


def _print_single_ticket(ticket: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(ticket, indent=2))
        return

    row = _ticket_row(ticket)
    ticket_id = row["TicketID"]
    title = row["TicketTitle"] or ""
    customer = row["CustomerName"] or "-"
    tech = row["TechnicianFullName"] or "Unassigned"
    priority = row["TicketPriority"] or "-"
    status = row["TicketStatus"] or "-"
    print(f"Ticket #{ticket_id}")
    print(f"  Title:       {title}")
    print(f"  Status:      {status}")
    print(f"  Priority:    {priority}")
    print(f"  Customer:    {customer}")
    print(f"  Technician:  {tech}")


def _run_tickets_list(args: argparse.Namespace) -> int:
    """Handle `tickets list` — status via API, priority client-side."""
    try:
        client = AteraClient()
        tickets = client.list_tickets(ticket_status=args.status)
        tickets = filter_by_priority(tickets, args.priority)
        _print_ticket_list(tickets, args.format)
        return 0
    except AteraError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _run_tickets_get(args: argparse.Namespace) -> int:
    """Handle `tickets get <ticket_id>`."""
    try:
        client = AteraClient()
        ticket = client.get_ticket(args.ticket_id)
        _print_single_ticket(ticket, args.format)
        return 0
    except AteraError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _run_tickets_resolution_rate(args: argparse.Namespace) -> int:
    """Handle `tickets resolution-rate`."""
    try:
        client = AteraClient()
        tickets = client.list_status_modified_tickets(include_comments=False)
        windowed = filter_by_window(tickets, args.since, args.until)
        metrics = compute_resolution_rate(windowed)
        _print_resolution_rate(metrics, args.format)
        return 0
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except AteraError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry point. Returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "tickets" and args.tickets_command == "list":
        return _run_tickets_list(args)

    if args.command == "tickets" and args.tickets_command == "get":
        return _run_tickets_get(args)

    if args.command == "tickets" and args.tickets_command == "resolution-rate":
        return _run_tickets_resolution_rate(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
