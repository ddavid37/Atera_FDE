"""Tests for atera_cli.client.AteraClient."""

import unittest

from atera_cli.client import AteraClient


class AteraClientTests(unittest.TestCase):
    @unittest.skip("AteraClient.list_tickets not implemented yet")
    def test_list_tickets_returns_plain_dicts(self) -> None:
        pass

    @unittest.skip("AteraClient retry/backoff not implemented yet")
    def test_retries_on_429_honoring_retry_after(self) -> None:
        pass


if __name__ == "__main__":
    unittest.main()
