"""HTTP client for the Atera Public API v3.

AteraClient owns authentication, base URL, gzip negotiation, and
retry/backoff behavior for rate limiting (HTTP 429, honoring
Retry-After) and transient server errors. It exposes one method per
API resource this project needs; callers never see raw
requests.Response objects, only plain dicts/lists.

Pagination bookkeeping is delegated to atera_cli.pagination.paginate;
this module only supplies the per-page fetch function.
"""

import os
import time
from typing import Any, Optional

import requests
from dotenv import load_dotenv

from atera_cli.exceptions import AteraAPIError, AteraRateLimitError
from atera_cli.pagination import paginate

API_BASE_URL = "https://api.atera.com"
MAX_RETRIES = 3


class AteraClient:
    """Thin wrapper around the Atera Public API v3."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = API_BASE_URL) -> None:
        """Create a client using the given API key, or `atera_api_key` from the environment/.env file."""
        load_dotenv()
        self._api_key = api_key or os.environ.get("atera_api_key")
        self._base_url = base_url
        self._session = requests.Session()

    def _get(self, path: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Perform an authenticated GET against the Atera API and return parsed JSON."""
        url = f"{self._base_url}{path}"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept-Encoding": "gzip",
        }
        for attempt in range(MAX_RETRIES):
            response = self._session.get(url, headers=headers, params=params)
            if response.status_code == 429:
                if attempt == MAX_RETRIES - 1:
                    raise AteraRateLimitError(f"Rate limited after {MAX_RETRIES} attempts: {path}")
                retry_after = int(response.headers.get("Retry-After", 1))
                time.sleep(retry_after)
                continue
            if not response.ok:
                raise AteraAPIError(f"Atera API error {response.status_code} for {path}: {response.text}")
            return response.json()

    def list_tickets(
        self,
        customer_id: Optional[int] = None,
        ticket_status: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Return all tickets, optionally filtered by customer ID or ticket status.

        Wraps GET /api/v3/tickets, walking all pages via pagination.paginate.
        """

        filters: dict[str, Any] = {}
        if customer_id is not None:
            filters["customerId"] = customer_id
        if ticket_status is not None:
            filters["ticketStatus"] = ticket_status

        def fetch_page(page_number: int) -> dict[str, Any]:
            params = {**filters, "page": page_number, "itemsInPage": 50}
            return self._get("/api/v3/tickets", params=params)

        return list(paginate(fetch_page))

    def list_status_modified_tickets(self, include_comments: bool = False) -> list[dict[str, Any]]:
        """Return all resolved and closed tickets.

        Wraps GET /api/v3/tickets/statusmodified, walking all pages via
        pagination.paginate.
        """

        def fetch_page(page_number: int) -> dict[str, Any]:
            params = {"page": page_number, "itemsInPage": 50, "includeComments": include_comments}
            return self._get("/api/v3/tickets/statusmodified", params=params)

        return list(paginate(fetch_page))

    def get_ticket(self, ticket_id: int) -> dict[str, Any]:
        """Return a single ticket by its ID.

        Wraps GET /api/v3/tickets/{ticketId}.
        """
        return self._get(f"/api/v3/tickets/{ticket_id}")
