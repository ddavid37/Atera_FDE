"""Tests for atera_cli.client.AteraClient."""

import unittest
from unittest.mock import MagicMock, patch

from atera_cli.client import AteraClient
from atera_cli.exceptions import AteraAPIError, AteraRateLimitError


def make_response(status_code=200, json_data=None, headers=None, text=""):
    response = MagicMock()
    response.status_code = status_code
    response.ok = 200 <= status_code < 300
    response.json.return_value = json_data if json_data is not None else {}
    response.headers = headers or {}
    response.text = text
    return response


class AteraClientTests(unittest.TestCase):
    def test_get_ticket_returns_parsed_json(self) -> None:
        client = AteraClient(api_key="test-key")
        ticket = {"TicketID": 1, "TicketTitle": "Cannot log in"}

        with patch.object(client._session, "get", return_value=make_response(json_data=ticket)) as mock_get:
            result = client.get_ticket(1)

        self.assertEqual(result, ticket)
        called_url = mock_get.call_args.args[0]
        self.assertEqual(called_url, "https://api.atera.com/api/v3/tickets/1")
        headers = mock_get.call_args.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "Bearer test-key")

    def test_raises_atera_api_error_on_non_retryable_error_status(self) -> None:
        client = AteraClient(api_key="test-key")
        error_response = make_response(status_code=404, text="Ticket not found")

        with patch.object(client._session, "get", return_value=error_response):
            with self.assertRaises(AteraAPIError):
                client.get_ticket(999)

    @patch("atera_cli.client.time.sleep")
    def test_retries_on_429_honoring_retry_after(self, mock_sleep) -> None:
        client = AteraClient(api_key="test-key")
        rate_limited = make_response(status_code=429, headers={"Retry-After": "2"})
        success = make_response(status_code=200, json_data={"TicketID": 1})

        with patch.object(client._session, "get", side_effect=[rate_limited, success]):
            result = client.get_ticket(1)

        self.assertEqual(result, {"TicketID": 1})
        mock_sleep.assert_called_once_with(2)

    @patch("atera_cli.client.time.sleep")
    def test_raises_after_exhausting_retries_on_repeated_429(self, mock_sleep) -> None:
        client = AteraClient(api_key="test-key")
        always_rate_limited = make_response(status_code=429, headers={"Retry-After": "1"})

        with patch.object(client._session, "get", return_value=always_rate_limited):
            with self.assertRaises(AteraRateLimitError):
                client.get_ticket(1)

    def test_list_tickets_returns_items_across_pages(self) -> None:
        client = AteraClient(api_key="test-key")
        page1 = {"items": [{"TicketID": 1}], "page": 1, "totalPages": 2}
        page2 = {"items": [{"TicketID": 2}], "page": 2, "totalPages": 2}

        def fake_get(path, params=None):
            self.assertEqual(path, "/api/v3/tickets")
            return page1 if params["page"] == 1 else page2

        with patch.object(client, "_get", side_effect=fake_get):
            result = client.list_tickets()

        self.assertEqual(result, [{"TicketID": 1}, {"TicketID": 2}])

    def test_list_tickets_passes_filters_as_query_params(self) -> None:
        client = AteraClient(api_key="test-key")
        page = {"items": [], "page": 1, "totalPages": 1}
        seen_params = []

        def fake_get(path, params=None):
            seen_params.append(params)
            return page

        with patch.object(client, "_get", side_effect=fake_get):
            client.list_tickets(customer_id=42, ticket_status="Open")

        self.assertEqual(seen_params[0]["customerId"], 42)
        self.assertEqual(seen_params[0]["ticketStatus"], "Open")

    def test_list_status_modified_tickets_returns_items_across_pages(self) -> None:
        client = AteraClient(api_key="test-key")
        page1 = {"items": [{"TicketID": 5}], "page": 1, "totalPages": 2}
        page2 = {"items": [{"TicketID": 6}], "page": 2, "totalPages": 2}

        def fake_get(path, params=None):
            self.assertEqual(path, "/api/v3/tickets/statusmodified")
            return page1 if params["page"] == 1 else page2

        with patch.object(client, "_get", side_effect=fake_get):
            result = client.list_status_modified_tickets()

        self.assertEqual(result, [{"TicketID": 5}, {"TicketID": 6}])


if __name__ == "__main__":
    unittest.main()
