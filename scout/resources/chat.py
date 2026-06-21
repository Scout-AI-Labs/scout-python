"""OpenAI-compatible chat completions, optionally grounded with web search."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterator, List, TYPE_CHECKING

from ._base import APIResource, clean_body

if TYPE_CHECKING:
    from .._client import Scout


class ChatCompletions(APIResource):
    def create(self, messages: List[Dict[str, Any]], **params: Any) -> Any:
        """Create a chat completion.

        Shape mirrors the OpenAI Chat Completions API; set ``web_search=True``
        to ground the answer in live results.
        """
        body = clean_body({"messages": messages, **params})
        return self._client.request("POST", "/v1/chat/completions", body=body)

    def stream(self, messages: List[Dict[str, Any]], **params: Any) -> Iterator[Any]:
        """Stream a chat completion as OpenAI-style ``chat.completion.chunk`` dicts.

        Read token text from ``chunk["choices"][0]["delta"]["content"]``.

            >>> for chunk in client.chat.completions.stream([{"role": "user", "content": "hi"}]):
            ...     print(chunk["choices"][0]["delta"].get("content", ""), end="")
        """
        body = clean_body({"messages": messages, "stream": True, **params})
        for evt in self._client.stream("POST", "/v1/chat/completions", body=body):
            if evt["data"] == "[DONE]":
                return
            yield json.loads(evt["data"])


class Chat(APIResource):
    def __init__(self, client: "Scout") -> None:
        super().__init__(client)
        self.completions = ChatCompletions(client)
