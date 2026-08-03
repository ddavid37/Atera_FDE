"""Tests for atera_cli.analytics.tickets."""

import unittest

from atera_cli.analytics.tickets import (
    compute_resolution_rate,
    filter_by_window,
    is_robin_resolved,
)


class TicketAnalyticsTests(unittest.TestCase):
    @unittest.skip("is_robin_resolved not implemented yet")
    def test_is_robin_resolved_when_technician_id_is_negative_one(self) -> None:
        pass

    @unittest.skip("filter_by_window not implemented yet")
    def test_filter_by_window_excludes_tickets_outside_range(self) -> None:
        pass

    @unittest.skip("compute_resolution_rate not implemented yet")
    def test_compute_resolution_rate_counts_robin_and_technician_separately(self) -> None:
        pass


if __name__ == "__main__":
    unittest.main()
