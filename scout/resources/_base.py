"""Base class for resource groups."""

from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .._client import Scout


class APIResource:
    """Holds a back-reference to the client."""

    def __init__(self, client: "Scout") -> None:
        self._client = client


def clean_body(values: Dict[str, Any]) -> Dict[str, Any]:
    """Drop keys whose value is ``None`` so we never send explicit nulls."""
    return {k: v for k, v in values.items() if v is not None}
