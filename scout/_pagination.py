"""Offset-based auto-pagination.

Scout's list endpoints (``/v1/searches``, ``/v1/jobs``, ``/v1/lists/runs``,
``/v1/monitors``) take ``limit`` + ``offset``. ``auto_paginate`` walks every
page lazily so callers can iterate without managing offsets. It stops once a
page returns fewer than ``limit`` items.
"""

from __future__ import annotations

from typing import Any, Callable, Iterator, List

_COMMON_ITEM_KEYS = ("items", "data", "results", "searches", "runs", "jobs", "monitors")


def extract_items(payload: Any) -> List[Any]:
    """Pull the list of records out of a list response of unknown shape."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in _COMMON_ITEM_KEYS:
            value = payload.get(key)
            if isinstance(value, list):
                return value
        for value in payload.values():
            if isinstance(value, list):
                return value
    return []


def auto_paginate(
    fetch_page: Callable[[int, int], Any],
    *,
    limit: int = 50,
    offset: int = 0,
) -> Iterator[Any]:
    """Yield every item across pages.

    ``fetch_page(limit, offset)`` should return a raw list response; the item
    list is extracted automatically.
    """
    while True:
        page = fetch_page(limit, offset)
        items = extract_items(page)
        for item in items:
            yield item
        if len(items) < limit:
            return
        offset += len(items)
