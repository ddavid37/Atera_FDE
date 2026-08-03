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
from typing import Any, Optional

import requests
from dotenv import load_dotenv

from atera_cli.pagination import paginate

API_BASE_URL = "https://api.atera.com"


class AteraClient:
    """Thin wrapper around the Atera Public API v3."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = API_BASE_URL) -> None:
        """Create a client using the given API key, or `atera_api_key` from the environment/.env file."""
        load_dotenv()
        self._api_key = api_key or os.environ.get("atera_api_key")
        self._base_url = base_url
        self._session = requests.Session()

    def list_tickets(
        self,
        customer_id: Optional[int] = None,
        ticket_status: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Return all tickets, optionally filtered by customer ID or ticket status.

        Wraps GET /api/v3/tickets, walking all pages via pagination.paginate.
        """
        raise NotImplementedError

    def list_status_modified_tickets(self, include_comments: bool = False) -> list[dict[str, Any]]:
        """Return all resolved and closed tickets.

        Wraps GET /api/v3/tickets/statusmodified, walking all pages via
        pagination.paginate.
        """
        raise NotImplementedError

    def get_ticket(self, ticket_id: int) -> dict[str, Any]:
        """Return a single ticket by its ID.

        Wraps GET /api/v3/tickets/{ticketId}.
        """
        raise NotImplementedError
