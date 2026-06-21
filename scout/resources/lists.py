"""Find-all ("lists"): build a list of entities matching a query, then enrich
or extend the run."""

from __future__ import annotations

from typing import Any, Dict, Iterator, Optional, TYPE_CHECKING

from .._pagination import auto_paginate
from ._base import APIResource, clean_body

if TYPE_CHECKING:
    from .._client import Scout


class ListRuns(APIResource):
    """Operations on async find-all runs."""

    def list(self, *, limit: Optional[int] = None, offset: Optional[int] = None) -> Any:
        return self._client.request(
            "GET", "/v1/lists/runs", query={"limit": limit, "offset": offset}
        )

    def iterate(self, *, limit: int = 50) -> Iterator[Any]:
        return auto_paginate(
            lambda lim, off: self.list(limit=lim, offset=off), limit=limit
        )

    def get(self, findall_id: str) -> Any:
        return self._client.request("GET", f"/v1/lists/runs/{findall_id}")

    def cancel(self, findall_id: str) -> Any:
        return self._client.request("POST", f"/v1/lists/runs/{findall_id}/cancel")

    def enrich(self, findall_id: str, **body: Any) -> Any:
        """Enrich the run's entities with additional fields."""
        return self._client.request(
            "POST", f"/v1/lists/runs/{findall_id}/enrich", body=clean_body(body)
        )

    def extend(self, findall_id: str, **body: Any) -> Any:
        """Extend the run with more matching entities."""
        return self._client.request(
            "POST", f"/v1/lists/runs/{findall_id}/extend", body=clean_body(body)
        )

    def events(self, findall_id: str) -> Any:
        return self._client.request("GET", f"/v1/lists/runs/{findall_id}/events")


class Lists(APIResource):
    def __init__(self, client: "Scout") -> None:
        super().__init__(client)
        self.runs = ListRuns(client)

    def create(self, query: str, **params: Any) -> Any:
        """Run a find-all synchronously.

        Pass a ``query`` plus optional ``fields`` or an ``output_schema`` to
        shape each entity.
        """
        body = clean_body({"query": query, **params})
        return self._client.request("POST", "/v1/lists", body=body)

    def run(self, query: str, **params: Any) -> Any:
        """Start an async find-all run; poll ``runs.get(id)`` for progress."""
        body = clean_body({"query": query, **params})
        return self._client.request("POST", "/v1/lists/runs", body=body)
