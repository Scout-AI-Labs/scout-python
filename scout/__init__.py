"""Scout - official Python SDK.

    >>> from scout import Scout
    >>> client = Scout()  # reads SCOUT_API_KEY
    >>> client.search.create(["climate tech startups"])
"""

from ._client import Scout
from ._version import __version__, API_VERSION
from ._errors import (
    ScoutError,
    APIError,
    ConnectionError,
    TimeoutError,
    BadRequestError,
    AuthenticationError,
    InsufficientCreditsError,
    PermissionDeniedError,
    NotFoundError,
    ConflictError,
    UnprocessableEntityError,
    RateLimitError,
    InternalServerError,
)

__all__ = [
    "Scout",
    "__version__",
    "API_VERSION",
    "ScoutError",
    "APIError",
    "ConnectionError",
    "TimeoutError",
    "BadRequestError",
    "AuthenticationError",
    "InsufficientCreditsError",
    "PermissionDeniedError",
    "NotFoundError",
    "ConflictError",
    "UnprocessableEntityError",
    "RateLimitError",
    "InternalServerError",
]
