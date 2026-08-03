"""Tests for atera_cli.pagination.paginate."""

import unittest

from atera_cli.pagination import paginate


class PaginateTests(unittest.TestCase):
    def test_yields_items_across_all_pages(self) -> None:
        pages = {
            1: {"items": [1, 2], "page": 1, "totalPages": 2},
            2: {"items": [3], "page": 2, "totalPages": 2},
        }
        calls = []

        def fetch_page(page_number: int) -> dict:
            calls.append(page_number)
            return pages[page_number]

        result = list(paginate(fetch_page))

        self.assertEqual(result, [1, 2, 3])
        self.assertEqual(calls, [1, 2])

    def test_stops_on_empty_page(self) -> None:
        # totalPages claims 3 pages, but page 2 comes back empty (stale
        # metadata). paginate must not loop forever or call page 3.
        pages = {
            1: {"items": [1, 2], "page": 1, "totalPages": 3},
            2: {"items": [], "page": 2, "totalPages": 3},
        }
        calls = []

        def fetch_page(page_number: int) -> dict:
            calls.append(page_number)
            return pages[page_number]

        result = list(paginate(fetch_page))

        self.assertEqual(result, [1, 2])
        self.assertEqual(calls, [1, 2])


if __name__ == "__main__":
    unittest.main()
