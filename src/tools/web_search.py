"""Just-in-time web search.

Uses DuckDuckGo (no API key required). Results are short, source-attributed
snippets the retriever agent can cite to the user. We always degrade to a
small set of canned suggestions if the network or library is unavailable, so
the demo never shows an empty state.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..config import settings


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str  # "ddg" | "fallback"


_FALLBACK_RESULTS: list[SearchResult] = [
    SearchResult(
        title="CISA — Cybersecurity Workforce",
        url="https://www.cisa.gov/cybersecurity-workforce",
        snippet="US gov't workforce framework with role definitions and skill maps.",
        source="fallback",
    ),
    SearchResult(
        title="NIST NICE Framework",
        url="https://niccs.cisa.gov/workforce-development/nice-framework",
        snippet="Standard taxonomy of cybersecurity work roles, tasks, and KSAs.",
        source="fallback",
    ),
    SearchResult(
        title="Cyberseek — Career Pathways",
        url="https://www.cyberseek.org/pathway.html",
        snippet="Interactive career path map: feeder roles → entry → mid → advanced.",
        source="fallback",
    ),
]


def web_search(query: str, *, max_results: int = 5) -> list[SearchResult]:
    if not settings.enable_web_search:
        return _FALLBACK_RESULTS[:max_results]

    try:
        try:
            from ddgs import DDGS  # newer package name
        except ImportError:
            from duckduckgo_search import DDGS  # legacy fallback
    except Exception:
        return _FALLBACK_RESULTS[:max_results]

    out: list[SearchResult] = []
    try:
        with DDGS() as ddgs:
            for hit in ddgs.text(query, max_results=max_results, safesearch="moderate"):
                out.append(
                    SearchResult(
                        title=(hit.get("title") or "").strip(),
                        url=(hit.get("href") or hit.get("url") or "").strip(),
                        snippet=(hit.get("body") or "").strip(),
                        source="ddg",
                    )
                )
    except Exception:
        return _FALLBACK_RESULTS[:max_results]

    return out or _FALLBACK_RESULTS[:max_results]


def format_results_for_prompt(results: Iterable[SearchResult]) -> str:
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r.title}\n    {r.url}\n    {r.snippet}")
    return "\n".join(lines) if lines else "(no live web results)"
