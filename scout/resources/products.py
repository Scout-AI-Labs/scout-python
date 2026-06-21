"""Product extraction from storefronts."""

from __future__ import annotations

from typing import Any

from ._base import APIResource, clean_body


class Products(APIResource):
    def extract(self, url: str, **params: Any) -> Any:
        """Crawl a store and extract its products.

        Bound the crawl with ``max_pages`` and ``max_depth``; steer it with
        ``instructions``.
        """
        body = clean_body({"url": url, **params})
        return self._client.request("POST", "/v1/products", body=body)

    def one(self, url: str, **params: Any) -> Any:
        """Extract a single product from one product-detail URL."""
        body = clean_body({"url": url, **params})
        return self._client.request("POST", "/v1/products/one", body=body)
