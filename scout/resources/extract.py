"""Multi-URL structured extraction."""

from __future__ import annotations

from typing import Any, List

from ._base import APIResource, clean_body


class Extract(APIResource):
    def create(self, urls: List[str], **params: Any) -> Any:
        """Extract structured data from one or more URLs.

        Provide an ``objective`` or an ``output_schema`` (JSON Schema) to shape
        the result; set ``find_via_search=True`` with ``search_queries`` to
        discover URLs first.

        Example:
            >>> scout.extract.create(
            ...     ["https://example.com/pricing"],
            ...     output_schema={"type": "object", "properties": {"plans": {"type": "array"}}},
            ... )
        """
        body = clean_body({"urls": urls, **params})
        return self._client.request("POST", "/v1/extract", body=body)
