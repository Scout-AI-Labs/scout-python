"""Web search, agentic AI queries, and search-run history."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional

from .._pagination import auto_paginate
from ._base import APIResource, clean_body


class Search(APIResource):
    def create(self, queries: List[str], **params: Any) -> Any:
        """Run a web search.

        Args:
            queries: One or more search queries.
            **params: ``objective``, ``depth``, ``mode``, ``category``,
                ``limit``, ``country``, ``location``, ``language``,
                ``freshness``, ``include_domains``, ``exclude_domains``,
                ``webhook``, ...

        Example:
            >>> scout.search.create(["climate tech startups"], depth="standard")
        """
        body = clean_body({"queries": queries, **params})
        return self._client.request("POST", "/v1/search", body=body)

    def ai_query(self, url: str, question: str, **params: Any) -> Any:
        """Answer a natural-language question by reading a page (and its links)."""
        body = clean_body({"url": url, "question": question, **params})
        return self._client.request("POST", "/v1/ai-query", body=body)

    def list(self, *, limit: Optional[int] = None, offset: Optional[int] = None) -> Any:
        """List prior search runs (most recent first)."""
        return self._client.request(
            "GET", "/v1/searches", query={"limit": limit, "offset": offset}
        )

    def iterate(self, *, limit: int = 50) -> Iterator[Any]:
        """Auto-paginating iterator over all search runs."""
        return auto_paginate(
            lambda lim, off: self.list(limit=lim, offset=off), limit=limit
        )

    def get(self, search_id: str) -> Any:
        """Fetch a single search run by id."""
        return self._client.request("GET", f"/v1/searches/{search_id}")

    def cancel(self, search_id: str) -> Any:
        """Cancel an in-flight search run."""
        return self._client.request("POST", f"/v1/searches/{search_id}/cancel")

    def events(self, search_id: str) -> Any:
        """Fetch the event stream (as JSON) for a search run."""
        return self._client.request("GET", f"/v1/searches/{search_id}/events")
