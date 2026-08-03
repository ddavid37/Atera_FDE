"""Generic pagination helper for Atera list endpoints.

Every Atera list endpoint returns the same envelope shape:

    {"items": [...], "page": int, "itemsInPage": int,
     "totalItemCount": int, "totalPages": int,
     "prevLink": str, "nextLink": str}

This module walks that envelope so resource methods on AteraClient
don't each need to repeat page-loop bookkeeping.
"""

from typing import Any, Callable, Iterator

# A page fetcher takes a 1-based page number and returns one envelope dict.
PageFetcher = Callable[[int], dict[str, Any]]


def paginate(fetch_page: PageFetcher, start_page: int = 1) -> Iterator[dict[str, Any]]:
    """Yield items across all pages by repeatedly calling fetch_page(page_number).

    Stops once the reported page count is exhausted or a page comes back
    with no items, whichever happens first.
    """
    raise NotImplementedError
