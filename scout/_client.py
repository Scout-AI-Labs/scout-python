"""Core HTTP client for the Scout API.

Zero runtime dependencies: built entirely on the Python standard library
(``urllib``). Resource groups (search, page, extract, ...) hang off the
``Scout`` client and call the shared ``request()`` method, which handles auth
headers, JSON encoding, timeouts, retries with exponential backoff + jitter,
idempotency keys, and error mapping.
"""

from __future__ import annotations

import builtins
import json
import os
import random
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from typing import Any, Dict, Mapping, Optional

from ._errors import (
    ConnectionError,
    ScoutError,
    TimeoutError,
    api_error_from_status,
)
from ._version import API_VERSION, __version__
from .resources.search import Search
from .resources.page import Page
from .resources.extract import Extract
from .resources.company import Company
from .resources.lists import Lists
from .resources.products import Products
from .resources.site import Site
from .resources.jobs import Jobs
from .resources.monitors import Monitors
from .resources.chat import Chat

DEFAULT_BASE_URL = "https://core.usescout.sh"
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 2
_RETRY_STATUSES = frozenset({408, 409, 429, 500, 502, 503, 504})


class Scout:
    """Client for the Scout web-intelligence API.

    Args:
        api_key: API key. Defaults to the ``SCOUT_API_KEY`` environment variable.
        base_url: API origin. Defaults to ``https://core.usescout.sh``.
        timeout: Per-request timeout in seconds. Defaults to 60.
        max_retries: Max automatic retries for transient failures. Defaults to 2.
        default_headers: Extra headers merged into every request.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        api_key = api_key or os.environ.get("SCOUT_API_KEY")
        if not api_key:
            raise ScoutError(
                "Missing API key. Pass api_key=... or set the "
                "SCOUT_API_KEY environment variable."
            )
        self._api_key = api_key
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._default_headers = dict(default_headers or {})

        # Resource groups - a faithful 1:1 mirror of the REST API tags.
        self.search = Search(self)
        self.page = Page(self)
        self.extract = Extract(self)
        self.company = Company(self)
        self.lists = Lists(self)
        self.products = Products(self)
        self.site = Site(self)
        self.jobs = Jobs(self)
        self.monitors = Monitors(self)
        self.chat = Chat(self)

    def with_options(self, **overrides: Any) -> "Scout":
        """Return a copy of the client with some config overridden."""
        return Scout(
            self._api_key,
            base_url=overrides.get("base_url", self.base_url),
            timeout=overrides.get("timeout", self.timeout),
            max_retries=overrides.get("max_retries", self.max_retries),
            default_headers=overrides.get("default_headers", self._default_headers),
        )

    # ------------------------------------------------------------------ #
    # Request plumbing
    # ------------------------------------------------------------------ #

    def request(
        self,
        method: str,
        path: str,
        *,
        body: Any = None,
        query: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        idempotency_key: Optional[str] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        """Issue a request with retries and typed error mapping."""
        retries = self.max_retries if max_retries is None else max_retries
        is_write = method != "GET"
        url = self._build_url(path, query)
        body_bytes = (
            json.dumps(body).encode("utf-8")
            if body is not None and method != "GET"
            else None
        )
        req_headers = self._build_headers(body_bytes, is_write, idempotency_key, headers)

        attempt = 0
        while True:
            try:
                return self._attempt(method, url, req_headers, body_bytes, timeout)
            except ScoutError as err:
                if not self._is_retriable(err) or attempt >= retries:
                    raise
                time.sleep(self._backoff_seconds(attempt, err))
                attempt += 1

    def _attempt(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        body_bytes: Optional[bytes],
        timeout: Optional[float],
    ) -> Any:
        req = urllib.request.Request(
            url, data=body_bytes, headers=headers, method=method
        )
        eff_timeout = self.timeout if timeout is None else timeout
        try:
            with urllib.request.urlopen(req, timeout=eff_timeout) as resp:
                status = resp.status
                raw = resp.read()
                resp_headers = {k.lower(): v for k, v in resp.headers.items()}
        except urllib.error.HTTPError as e:
            status = e.code
            raw = e.read()
            resp_headers = {k.lower(): v for k, v in (e.headers or {}).items()}
        except (socket.timeout, builtins.TimeoutError) as e:
            raise TimeoutError(f"Request timed out after {eff_timeout}s") from e
        except urllib.error.URLError as e:
            reason = getattr(e, "reason", e)
            if isinstance(reason, socket.timeout):
                raise TimeoutError(f"Request timed out after {eff_timeout}s") from e
            raise ConnectionError(str(reason)) from e
        except OSError as e:  # connection reset, broken pipe, etc.
            raise ConnectionError(str(e)) from e

        return self._parse_response(status, raw, resp_headers)

    def _parse_response(
        self, status: int, raw: bytes, headers: Dict[str, str]
    ) -> Any:
        request_id = headers.get("x-request-id")
        if status == 204 or not raw:
            parsed: Any = None
        else:
            text = raw.decode("utf-8", errors="replace")
            ctype = headers.get("content-type", "")
            if "json" in ctype:
                try:
                    parsed = json.loads(text)
                except ValueError:
                    parsed = text
            else:
                parsed = text

        if 200 <= status < 300:
            return parsed

        raise api_error_from_status(
            status,
            _error_message(parsed, status),
            request_id=request_id,
            body=parsed,
            code=_error_code(parsed),
            headers=headers,
        )

    def _build_url(self, path: str, query: Optional[Mapping[str, Any]]) -> str:
        url = self.base_url + path
        if query:
            pairs = []
            for key, value in query.items():
                if value is None:
                    continue
                if isinstance(value, (list, tuple)):
                    pairs.extend((key, str(v)) for v in value)
                else:
                    pairs.append((key, str(value)))
            if pairs:
                url += "?" + urllib.parse.urlencode(pairs)
        return url

    def _build_headers(
        self,
        body_bytes: Optional[bytes],
        is_write: bool,
        idempotency_key: Optional[str],
        extra: Optional[Mapping[str, str]],
    ) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
            "User-Agent": f"scout-python/{__version__}",
            "Scout-Version": API_VERSION,
        }
        headers.update(self._default_headers)
        if extra:
            headers.update(extra)
        if body_bytes is not None:
            headers["Content-Type"] = "application/json"
        if is_write:
            headers["Idempotency-Key"] = idempotency_key or str(uuid.uuid4())
        return headers

    def _is_retriable(self, err: ScoutError) -> bool:
        if isinstance(err, TimeoutError):
            return True
        if isinstance(err, ConnectionError):
            return True
        if err.status is not None:
            return err.status in _RETRY_STATUSES
        return False

    def _backoff_seconds(self, attempt: int, err: ScoutError) -> float:
        retry_after = err.headers.get("retry-after")
        if retry_after:
            try:
                return min(float(retry_after), 60.0)
            except ValueError:
                pass
        base = min(0.5 * (2 ** attempt), 8.0)
        return base * (0.5 + random.random() * 0.5)


def _error_message(body: Any, status: int) -> str:
    if isinstance(body, dict):
        detail = body.get("detail") or body.get("error") or body.get("message")
        if isinstance(detail, str):
            return detail
        if isinstance(detail, dict) and isinstance(detail.get("message"), str):
            return detail["message"]
    if isinstance(body, str) and body:
        return body
    return f"Scout API returned HTTP {status}"


def _error_code(body: Any) -> Optional[str]:
    if isinstance(body, dict):
        if isinstance(body.get("code"), str):
            return body["code"]
        err = body.get("error")
        if isinstance(err, dict) and isinstance(err.get("code"), str):
            return err["code"]
    return None
