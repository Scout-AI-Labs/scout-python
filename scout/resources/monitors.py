"""Scheduled searches ("monitors"): run a query on a cadence and receive new
results via webhook."""

from __future__ import annotations

from typing import Any, Iterator, Optional

from .._pagination import auto_paginate
from ._base import APIResource, clean_body


class Monitors(APIResource):
    def create(self, query: str, **params: Any) -> Any:
        """Create a monitor with a ``query`` and a ``cadence`` or ``cron`` schedule."""
        body = clean_body({"query": query, **params})
        return self._client.request("POST", "/v1/monitors", body=body)

    def list(self, *, limit: Optional[int] = None, offset: Optional[int] = None) -> Any:
        """List monitors."""
        return self._client.request(
            "GET", "/v1/monitors", query={"limit": limit, "offset": offset}
        )

    def iterate(self, *, limit: int = 50) -> Iterator[Any]:
        """Auto-paginating iterator over all monitors."""
        return auto_paginate(
            lambda lim, off: self.list(limit=lim, offset=off), limit=limit
        )

    def get(self, monitor_id: str) -> Any:
        """Fetch a monitor by id."""
        return self._client.request("GET", f"/v1/monitors/{monitor_id}")

    def update(self, monitor_id: str, **params: Any) -> Any:
        """Update a monitor's query, schedule, or webhook."""
        body = clean_body(params)
        return self._client.request("PATCH", f"/v1/monitors/{monitor_id}", body=body)

    def delete(self, monitor_id: str) -> Any:
        """Delete a monitor."""
        return self._client.request("DELETE", f"/v1/monitors/{monitor_id}")

    def pause(self, monitor_id: str) -> Any:
        """Pause a monitor."""
        return self._client.request("POST", f"/v1/monitors/{monitor_id}/pause")

    def resume(self, monitor_id: str) -> Any:
        """Resume a paused monitor."""
        return self._client.request("POST", f"/v1/monitors/{monitor_id}/resume")

    def run(self, monitor_id: str) -> Any:
        """Trigger a monitor run immediately."""
        return self._client.request("POST", f"/v1/monitors/{monitor_id}/run")

    def events(self, monitor_id: str) -> Any:
        """Fetch a monitor's events."""
        return self._client.request("GET", f"/v1/monitors/{monitor_id}/events")

    def stream_events(self, monitor_id: str) -> Iterator[Any]:
        """Stream a monitor's events live (SSE)."""
        return self._stream_sse(f"/v1/monitors/{monitor_id}/events")
