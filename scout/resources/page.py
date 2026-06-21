"""Single-page operations: markdown, html, screenshot, images, extract."""

from __future__ import annotations

from typing import Any

from ._base import APIResource, clean_body


class Page(APIResource):
    def markdown(self, url: str, **params: Any) -> Any:
        """Fetch a page rendered to clean Markdown."""
        body = clean_body({"url": url, **params})
        return self._client.request("POST", "/v1/page/markdown", body=body)

    def html(self, url: str, **params: Any) -> Any:
        """Fetch a page's HTML."""
        body = clean_body({"url": url, **params})
        return self._client.request("POST", "/v1/page/html", body=body)

    def screenshot(self, url: str, **params: Any) -> Any:
        """Capture a screenshot of a page.

        Tune ``viewport_width``/``viewport_height``, ``full_page``, ``format``,
        ``wait_ms``, ``inline``, ``element_selector``, ``dismiss_overlays``.
        """
        body = clean_body({"url": url, **params})
        return self._client.request("POST", "/v1/page/screenshot", body=body)

    def images(self, url: str, **params: Any) -> Any:
        """Extract the images on a page, with optional inline data URIs."""
        body = clean_body({"url": url, **params})
        return self._client.request("POST", "/v1/page/images", body=body)

    def extract(self, url: str, **params: Any) -> Any:
        """Structured extraction scoped to a single page."""
        body = clean_body({"url": url, **params})
        return self._client.request("POST", "/v1/page/extract", body=body)
