"""Whole-site operations: crawl and sitemap discovery."""

from __future__ import annotations

from typing import Any

from ._base import APIResource, clean_body


class Site(APIResource):
    def crawl(self, start_url: str, **params: Any) -> Any:
        """Crawl a site from ``start_url``.

        Bound it with ``max_pages``/``max_depth`` and scope it with
        ``same_host_only``, ``include_patterns``, ``exclude_patterns``.
        """
        body = clean_body({"start_url": start_url, **params})
        return self._client.request("POST", "/v1/site/crawl", body=body)

    def map(self, start_url: str, **params: Any) -> Any:
        """Discover a site's URLs (sitemap) from ``start_url``."""
        body = clean_body({"start_url": start_url, **params})
        return self._client.request("POST", "/v1/site/map", body=body)
