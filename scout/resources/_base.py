"""Base class for resource groups."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterator, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .._client import Scout


class APIResource:
    """Holds a back-reference to the client."""

    def __init__(self, client: "Scout") -> None:
        self._client = client

    def _stream_sse(self, path: str) -> Iterator[Any]:
        """Yield each SSE event's parsed JSON from a GET stream endpoint."""
        for evt in self._client.stream("GET", path):
            if evt["data"] == "[DONE]":
                return
            yield json.loads(evt["data"])


def clean_body(values: Dict[str, Any]) -> Dict[str, Any]:
    """Drop keys whose value is ``None`` so we never send explicit nulls."""
    return {k: v for k, v in values.items() if v is not None}
