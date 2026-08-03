"""Custom exception types for the Atera CLI toolkit.

Kept in their own module (rather than defined inside client.py) so
other layers, such as analytics or cli, can catch or reference specific
error types without importing the HTTP client implementation itself.
"""


class AteraError(Exception):
    """Base class for all errors raised by this toolkit."""


class AteraAPIError(AteraError):
    """Raised when the Atera API returns an unexpected error response."""


class AteraRateLimitError(AteraAPIError):
    """Raised when the Atera API returns HTTP 429 Too Many Requests."""
