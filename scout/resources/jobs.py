"""Async tasks ("jobs"): submit a natural-language task, then poll the task or
stream its events until it completes."""

from __future__ import annotations

from typing import Any, Iterator, Optional

from .._pagination import auto_paginate
from ._base import APIResource, clean_body


class Jobs(APIResource):
    def create(self, task: str, **params: Any) -> Any:
        """Submit a job. Returns a task id to poll with ``get(task_id)``."""
        body = clean_body({"task": task, **params})
        return self._client.request("POST", "/v1/jobs", body=body)

    def list(self, *, limit: Optional[int] = None, offset: Optional[int] = None) -> Any:
        """List jobs (most recent first)."""
        return self._client.request(
            "GET", "/v1/jobs", query={"limit": limit, "offset": offset}
        )

    def iterate(self, *, limit: int = 50) -> Iterator[Any]:
        """Auto-paginating iterator over all jobs."""
        return auto_paginate(
            lambda lim, off: self.list(limit=lim, offset=off), limit=limit
        )

    def get(self, task_id: str) -> Any:
        """Fetch a job by task id."""
        return self._client.request("GET", f"/v1/jobs/{task_id}")

    def cancel(self, task_id: str) -> Any:
        """Cancel a running job."""
        return self._client.request("POST", f"/v1/jobs/{task_id}/cancel")

    def events(self, task_id: str) -> Any:
        """Fetch a job's events."""
        return self._client.request("GET", f"/v1/jobs/{task_id}/events")

    def start_run(self, **body: Any) -> Any:
        """Start a run for a job."""
        return self._client.request("POST", "/v1/jobs/runs", body=clean_body(body))

    def run_result(self, run_id: str) -> Any:
        """Fetch the result of a completed run."""
        return self._client.request("GET", f"/v1/jobs/runs/{run_id}")

    def run_events(self, run_id: str) -> Any:
        """Fetch a run's events."""
        return self._client.request("GET", f"/v1/jobs/runs/{run_id}/events")
