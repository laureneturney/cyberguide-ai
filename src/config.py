"""Centralized environment-driven configuration.

The app reads everything it needs from environment variables (typically loaded
from a local `.env` file via python-dotenv). This module is the single source
of truth — everywhere else in the codebase imports `settings` from here.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Literal

from dotenv import load_dotenv

load_dotenv(override=False)

ProviderName = Literal["watsonx", "custom", "mock"]


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _float(name: str, default: float) -> float:
    raw = os.getenv(name)
    try:
        return float(raw) if raw not in (None, "") else default
    except ValueError:
        return default


def _int(name: str, default: int) -> int:
    raw = os.getenv(name)
    try:
        return int(raw) if raw not in (None, "") else default
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    provider: ProviderName = "mock"

    watsonx_apikey: str = ""
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"
    watsonx_project_id: str = ""
    watsonx_model_id: str = "ibm/granite-3-8b-instruct"

    custom_base_url: str = "http://localhost:8080/v1"
    custom_api_key: str = "not-needed"
    custom_model: str = "llama-3.1-8b-instruct"

    enable_web_search: bool = True
    temperature: float = 0.3
    max_tokens: int = 900

    # Even when the backend provider is mock or custom, we surface "IBM watsonx"
    # to the user as the service brand. This is intentional UX, not a bug.
    display_provider_name: str = "IBM watsonx"

    extras: dict = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "Settings":
        provider_raw = (os.getenv("LLM_PROVIDER") or "mock").strip().lower()
        provider: ProviderName = provider_raw if provider_raw in ("watsonx", "custom", "mock") else "mock"
        return cls(
            provider=provider,
            watsonx_apikey=os.getenv("WATSONX_APIKEY", "").strip(),
            watsonx_url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com").strip(),
            watsonx_project_id=os.getenv("WATSONX_PROJECT_ID", "").strip(),
            watsonx_model_id=os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct").strip(),
            custom_base_url=os.getenv("CUSTOM_LLM_BASE_URL", "http://localhost:8080/v1").strip(),
            custom_api_key=os.getenv("CUSTOM_LLM_API_KEY", "not-needed").strip(),
            custom_model=os.getenv("CUSTOM_LLM_MODEL", "llama-3.1-8b-instruct").strip(),
            enable_web_search=_bool("ENABLE_WEB_SEARCH", True),
            temperature=_float("LLM_TEMPERATURE", 0.3),
            max_tokens=_int("LLM_MAX_TOKENS", 900),
        )

    def watsonx_ready(self) -> bool:
        return bool(self.watsonx_apikey and self.watsonx_project_id)

    def custom_ready(self) -> bool:
        return bool(self.custom_base_url and self.custom_model)


settings = Settings.from_env()
