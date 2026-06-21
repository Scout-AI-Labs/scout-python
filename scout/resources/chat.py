"""OpenAI-compatible chat completions, optionally grounded with web search."""

from __future__ import annotations

from typing import Any, Dict, List, TYPE_CHECKING

from ._base import APIResource, clean_body

if TYPE_CHECKING:
    from .._client import Scout


class ChatCompletions(APIResource):
    def create(self, messages: List[Dict[str, Any]], **params: Any) -> Any:
        """Create a chat completion.

        Shape mirrors the OpenAI Chat Completions API; set ``web_search=True``
        to ground the answer in live results.

        Note: streaming (``stream=True``) returns the raw response envelope in
        this release - consume ``/v1/chat/completions`` directly for SSE.
        """
        body = clean_body({"messages": messages, **params})
        return self._client.request("POST", "/v1/chat/completions", body=body)


class Chat(APIResource):
    def __init__(self, client: "Scout") -> None:
        super().__init__(client)
        self.completions = ChatCompletions(client)
