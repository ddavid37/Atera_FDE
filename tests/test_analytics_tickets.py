"""Tests for atera_cli.analytics.tickets."""

import unittest

from atera_cli.analytics.tickets import (
    compute_resolution_rate,
    filter_by_priority,
    filter_by_window,
    is_robin_resolved,
)


class TicketAnalyticsTests(unittest.TestCase):
    def test_is_robin_resolved_when_technician_id_is_negative_one(self) -> None:
        self.assertTrue(is_robin_resolved({"TechnicianContactID": -1}))
        self.assertFalse(is_robin_resolved({"TechnicianContactID": 42}))
        self.assertFalse(is_robin_resolved({}))

    def test_filter_by_window_excludes_tickets_outside_range(self) -> None:
        tickets = [
            {"TicketID": 1, "TicketResolvedDate": "2026-06-15T12:00:00.000Z"},
            {"TicketID": 2, "TicketResolvedDate": "2026-05-31T23:59:59.000Z"},
            {"TicketID": 3, "TicketResolvedDate": "2026-08-01T00:00:00.000Z"},
            {"TicketID": 4, "TicketResolvedDate": "2026-07-01T00:00:00.000Z"},
            {"TicketID": 5, "TicketResolvedDate": None},
            {"TicketID": 6},
        ]

        result = filter_by_window(tickets, since="2026-06-01", until="2026-08-01")

        self.assertEqual([t["TicketID"] for t in result], [1, 3, 4])

    def test_filter_by_window_rejects_inverted_range(self) -> None:
        with self.assertRaises(ValueError):
            filter_by_window([], since="2026-08-01", until="2026-06-01")

    def test_compute_resolution_rate_counts_robin_and_technician_separately(self) -> None:
        tickets = [
            {"TechnicianContactID": -1},
            {"TechnicianContactID": -1},
            {"TechnicianContactID": 7},
            {"TechnicianContactID": 9},
        ]

        metrics = compute_resolution_rate(tickets)

        self.assertEqual(metrics["total"], 4)
        self.assertEqual(metrics["robin"], 2)
        self.assertEqual(metrics["technician"], 2)
        self.assertEqual(metrics["robin_rate"], 0.5)
        self.assertEqual(metrics["technician_rate"], 0.5)

    def test_compute_resolution_rate_empty_set(self) -> None:
        metrics = compute_resolution_rate([])
        self.assertEqual(
            metrics,
            {
                "total": 0,
                "robin": 0,
                "technician": 0,
                "robin_rate": 0.0,
                "technician_rate": 0.0,
            },
        )

    def test_filter_by_priority_is_case_insensitive(self) -> None:
        tickets = [
            {"TicketID": 1, "TicketPriority": "Critical"},
            {"TicketID": 2, "TicketPriority": "High"},
            {"TicketID": 3, "TicketPriority": "critical"},
            {"TicketID": 4, "TicketPriority": "Low"},
        ]

        result = filter_by_priority(tickets, "Critical")

        self.assertEqual([t["TicketID"] for t in result], [1, 3])


if __name__ == "__main__":
    unittest.main()
