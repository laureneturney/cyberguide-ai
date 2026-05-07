"""Just-in-time resource retriever.

Gets candidates from two sources — the curated list and live web search —
then asks the LLM to rank/explain why each is the right fit *now*. The agent
never invents URLs: every URL it returns must come from the candidate pool.
"""
from __future__ import annotations

import json

from ..config import settings
from ..data import resources_for
from ..llm import LLMMessage, get_provider
from ..tools import web_search, format_results_for_prompt
from .prompts import RETRIEVER_SYSTEM
from .schemas import RetrievedResource, UserProfile


class RetrieverAgent:
    name = "retriever"

    def retrieve(
        self,
        profile: UserProfile,
        *,
        focus: str = "",
        max_results: int = 5,
    ) -> list[RetrievedResource]:
        curated = resources_for(
            role_id=profile.target_role or None,
            domain_id=profile.preferred_domain or None,
        )
        web_query = (
            focus
            or f"best free resources for {profile.target_role or 'cybersecurity entry-level'} in 2026"
        )
        web_hits = web_search(web_query, max_results=4) if settings.enable_web_search else []

        candidates_block = {
            "curated": [
                {
                    "title": r["title"],
                    "kind": r["kind"],
                    "url": r["url"],
                    "cost": r["cost"],
                    "time_estimate": r["time_estimate"],
                    "why_curated_match": "matches role/domain",
                }
                for r in curated[:8]
            ],
            "web": [
                {
                    "title": h.title,
                    "kind": "reference",
                    "url": h.url,
                    "snippet": h.snippet,
                    "source": h.source,
                }
                for h in web_hits
            ],
        }
        user = (
            "Pick 3-5 best resources for the user's CURRENT need. Use ONLY the URLs in the candidate pool.\n\n"
            f"User profile and focus:\n```json\n{json.dumps({'profile': profile.model_dump(), 'focus': focus}, indent=2)}\n```\n\n"
            f"Candidate pool:\n```json\n{json.dumps(candidates_block, indent=2)}\n```\n\n"
            f"Live search snippets (for reference only):\n{format_results_for_prompt(web_hits)}\n"
        )

        messages = [
            LLMMessage("system", RETRIEVER_SYSTEM),
            LLMMessage("user", user),
        ]
        parsed, _ = get_provider().complete_json(
            messages,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )
        items = (parsed or {}).get("resources") or []
        valid_urls = {r["url"] for r in candidates_block["curated"]} | {
            r["url"] for r in candidates_block["web"]
        }
        out: list[RetrievedResource] = []
        for it in items[:max_results]:
            if not isinstance(it, dict):
                continue
            url = (it.get("url") or "").strip()
            if url and valid_urls and url not in valid_urls:
                # If model invented a URL, drop it — never surface fabricated links.
                continue
            out.append(
                RetrievedResource(
                    title=str(it.get("title", "")).strip() or "Untitled",
                    kind=str(it.get("kind", "reference")),
                    url=url,
                    why=str(it.get("why", "")).strip(),
                    cost=str(it.get("cost", "")).strip(),
                    time_estimate=str(it.get("time_estimate", "")).strip(),
                    source="curated"
                    if url in {r["url"] for r in candidates_block["curated"]}
                    else "web",
                )
            )

        if not out:
            # Hard fallback: the curated top-N, no LLM in the loop.
            for r in curated[:max_results]:
                out.append(
                    RetrievedResource(
                        title=r["title"],
                        kind=r["kind"],
                        url=r["url"],
                        why=r["why"],
                        cost=r["cost"],
                        time_estimate=r["time_estimate"],
                        source="curated",
                    )
                )
        return out
