"""IBM watsonx.ai foundation-model provider.

Lazy-imports the SDK so missing credentials never break the demo (the factory
falls back to mock). Uses a single-prompt text-generation call — works across
Granite, Llama, and Mistral models hosted on watsonx.
"""
from __future__ import annotations

from typing import Any

from .base import LLMMessage, LLMProvider, LLMResponse, join_messages


class WatsonxLLM(LLMProvider):
    name = "watsonx"

    def __init__(
        self,
        api_key: str,
        url: str,
        project_id: str,
        model_id: str = "ibm/granite-3-8b-instruct",
    ) -> None:
        if not api_key or not project_id:
            raise RuntimeError("watsonx provider requires WATSONX_APIKEY and WATSONX_PROJECT_ID")
        self.model = model_id
        self._project_id = project_id
        self._url = url
        self._api_key = api_key
        self._client = self._build_client()

    def _build_client(self) -> Any:
        # Imported lazily so the package isn't required for mock/custom flows.
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference

        creds = Credentials(url=self._url, api_key=self._api_key)
        return ModelInference(
            model_id=self.model,
            credentials=creds,
            project_id=self._project_id,
        )

    def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.3,
        max_tokens: int = 800,
    ) -> LLMResponse:
        prompt = join_messages(messages)
        params = {
            "decoding_method": "greedy" if temperature <= 0.05 else "sample",
            "max_new_tokens": max_tokens,
            "temperature": float(max(0.01, min(temperature, 1.5))),
            "repetition_penalty": 1.05,
        }
        result = self._client.generate_text(prompt=prompt, params=params)
        # SDK returns a dict for some models, a string for others.
        text = ""
        if isinstance(result, str):
            text = result
        elif isinstance(result, dict):
            text = (
                (result.get("results") or [{}])[0].get("generated_text")
                or result.get("generated_text")
                or ""
            )
        return LLMResponse(text=text.strip(), provider=self.name, model=self.model)
