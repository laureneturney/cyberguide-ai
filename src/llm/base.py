"""Provider-agnostic LLM contract.

Every concrete provider implements a single `complete(...)` method that
takes a list of role-tagged messages and returns plain text. JSON-mode
helpers live on the base class so call sites stay clean.
"""
from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass
class LLMMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str
    usage: dict | None = None


class LLMProvider(ABC):
    name: str = "base"
    model: str = "unknown"

    @abstractmethod
    def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.3,
        max_tokens: int = 800,
    ) -> LLMResponse: ...

    def complete_json(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int = 800,
    ) -> tuple[Any, LLMResponse]:
        """Ask the model to return JSON; tolerantly parse what comes back.

        We don't trust providers to honor JSON mode flags, so we strip
        markdown fences and pull the first {...} or [...] block. On
        parse failure we return an empty dict alongside the raw response
        so callers can degrade gracefully.
        """
        response = self.complete(messages, temperature=temperature, max_tokens=max_tokens)
        parsed = _safe_json_parse(response.text)
        return parsed, response


def _safe_json_parse(text: str) -> Any:
    if not text:
        return {}
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    candidate = fenced.group(1).strip() if fenced else text.strip()
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass
    for opener, closer in (("{", "}"), ("[", "]")):
        start = candidate.find(opener)
        end = candidate.rfind(closer)
        if start != -1 and end > start:
            try:
                return json.loads(candidate[start : end + 1])
            except json.JSONDecodeError:
                continue
    return {}


def join_messages(messages: Iterable[LLMMessage]) -> str:
    """Cheap text serialization for providers that take a single prompt string."""
    parts = []
    for m in messages:
        tag = {"system": "[SYSTEM]", "user": "[USER]", "assistant": "[ASSISTANT]"}.get(
            m.role, f"[{m.role.upper()}]"
        )
        parts.append(f"{tag}\n{m.content}")
    parts.append("[ASSISTANT]\n")
    return "\n\n".join(parts)
