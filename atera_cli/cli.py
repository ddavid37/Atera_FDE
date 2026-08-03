"""Command-line interface for the Atera CLI toolkit.

This is the composition root: the only module that wires together
AteraClient (HTTP) and analytics functions (pure). It parses
arguments, dispatches to a command handler, and formats/prints output.
Command handlers here are stubs until the client and analytics layers
are implemented.
"""

import argparse
import sys
from typing import Optional, Sequence


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser and its subcommands."""
    parser = argparse.ArgumentParser(
        prog="atera_cli",
        description="Command-line tools for the Atera Public API.",
    )
    subparsers = parser.add_subparsers(dest="command")

    tickets_parser = subparsers.add_parser("tickets", help="Ticket-related commands")
    tickets_subparsers = tickets_parser.add_subparsers(dest="tickets_command")

    resolution_rate_parser = tickets_subparsers.add_parser(
        "resolution-rate",
        help="Compute the Robin vs. technician ticket resolution rate over a time window",
    )
    resolution_rate_parser.add_argument("--since", help="Window start date (YYYY-MM-DD)")
    resolution_rate_parser.add_argument("--until", help="Window end date (YYYY-MM-DD)")
    resolution_rate_parser.add_argument(
        "--format", choices=["table", "json"], default="table", help="Output format (default: table)"
    )

    return parser


def _run_tickets_resolution_rate(args: argparse.Namespace) -> int:
    """Handle `tickets resolution-rate`.

    Intended flow once implemented: build an AteraClient, call
    list_status_modified_tickets(), pass the result through
    analytics.tickets.filter_by_window() and compute_resolution_rate(),
    then print according to args.format.
    """
    print("tickets resolution-rate: not implemented yet")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry point. Returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "tickets" and args.tickets_command == "resolution-rate":
        return _run_tickets_resolution_rate(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
