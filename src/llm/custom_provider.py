"""OpenAI-compatible provider.

Works with anything that speaks OpenAI's `/v1/chat/completions` — vLLM,
Ollama (`/v1` shim), LM Studio, OpenAI itself, Together, Groq, etc. The
chat schema is universal enough that no per-vendor branching is needed.
"""
from __future__ import annotations

from .base import LLMMessage, LLMProvider, LLMResponse


class CustomLLM(LLMProvider):
    name = "custom"

    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        if not base_url or not model:
            raise RuntimeError("custom provider requires CUSTOM_LLM_BASE_URL and CUSTOM_LLM_MODEL")
        self.model = model
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key or "not-needed"
        self._client = self._build_client()

    def _build_client(self):
        from openai import OpenAI  # lazy import

        return OpenAI(base_url=self._base_url, api_key=self._api_key)

    def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.3,
        max_tokens: int = 800,
    ) -> LLMResponse:
        payload = [{"role": m.role, "content": m.content} for m in messages]
        completion = self._client.chat.completions.create(
            model=self.model,
            messages=payload,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = (completion.choices[0].message.content or "").strip()
        usage = getattr(completion, "usage", None)
        return LLMResponse(
            text=text,
            provider=self.name,
            model=self.model,
            usage=usage.model_dump() if usage and hasattr(usage, "model_dump") else None,
        )
