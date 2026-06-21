"""Error hierarchy for the Scout SDK.

Every failure surfaces as a ``ScoutError``. Network problems become
``ConnectionError`` / ``TimeoutError``; any non-2xx HTTP response becomes an
``APIError`` subclass chosen by status code. The raw status, parsed body, and
request id are always available so callers can branch on
``except RateLimitError`` or read ``err.status`` directly.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class ScoutError(Exception):
    """Base class for every error raised by the SDK."""

    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        request_id: Optional[str] = None,
        body: Any = None,
        code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.request_id = request_id
        self.body = body
        self.code = code
        self.headers = headers or {}


class ConnectionError(ScoutError):
    """No HTTP response was received (DNS, refused connection, reset)."""


class TimeoutError(ConnectionError):
    """The request exceeded the configured timeout before a response arrived."""


class APIError(ScoutError):
    """Base for every error carrying an HTTP status from the API."""


class BadRequestError(APIError):
    """400 - malformed request (bad params, invalid JSON)."""


class AuthenticationError(APIError):
    """401 - missing or invalid API key."""


class InsufficientCreditsError(APIError):
    """402 - the team is out of credits for this operation."""


class PermissionDeniedError(APIError):
    """403 - authenticated, but not allowed to perform this action."""


class NotFoundError(APIError):
    """404 - the resource (search id, job id, monitor id) does not exist."""


class ConflictError(APIError):
    """409 - the request conflicts with the current state of the resource."""


class UnprocessableEntityError(APIError):
    """422 - the request was well-formed but failed validation."""


class RateLimitError(APIError):
    """429 - rate limit exceeded. Inspect ``headers['retry-after']``."""


class InternalServerError(APIError):
    """>=500 - the Scout API failed to handle a valid request."""


_STATUS_MAP = {
    400: BadRequestError,
    401: AuthenticationError,
    402: InsufficientCreditsError,
    403: PermissionDeniedError,
    404: NotFoundError,
    409: ConflictError,
    422: UnprocessableEntityError,
    429: RateLimitError,
}


def api_error_from_status(
    status: int,
    message: str,
    *,
    request_id: Optional[str] = None,
    body: Any = None,
    code: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
) -> APIError:
    """Construct the most specific ``APIError`` for an HTTP status."""
    cls = _STATUS_MAP.get(status)
    if cls is None:
        cls = InternalServerError if status >= 500 else BadRequestError
    return cls(
        message,
        status=status,
        request_id=request_id,
        body=body,
        code=code,
        headers=headers,
    )
