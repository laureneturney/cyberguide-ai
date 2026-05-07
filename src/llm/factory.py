"""Pick a provider based on env config; fall back gracefully when creds/SDKs miss.

Resolution order:
  1. Honor the explicit LLM_PROVIDER setting.
  2. If the chosen provider is misconfigured (missing keys, missing SDK),
     fall back to the deterministic mock so the demo always renders.
"""
from __future__ import annotations

import functools
import logging

from ..config import settings
from .base import LLMProvider
from .mock_provider import MockLLM

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def get_provider() -> LLMProvider:
    chosen = settings.provider

    if chosen == "watsonx":
        if not settings.watsonx_ready():
            logger.warning("watsonx selected but credentials missing — using mock provider.")
            return MockLLM()
        try:
            from .watsonx_provider import WatsonxLLM

            return WatsonxLLM(
                api_key=settings.watsonx_apikey,
                url=settings.watsonx_url,
                project_id=settings.watsonx_project_id,
                model_id=settings.watsonx_model_id,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("watsonx init failed (%s); falling back to mock.", exc)
            return MockLLM()

    if chosen == "custom":
        if not settings.custom_ready():
            logger.warning("custom selected but config missing — using mock provider.")
            return MockLLM()
        try:
            from .custom_provider import CustomLLM

            return CustomLLM(
                base_url=settings.custom_base_url,
                api_key=settings.custom_api_key,
                model=settings.custom_model,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("custom init failed (%s); falling back to mock.", exc)
            return MockLLM()

    return MockLLM()


def reset_provider_cache() -> None:
    get_provider.cache_clear()
