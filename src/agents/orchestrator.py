"""Coordinates the four agents and exposes a small API the UI calls into.

The orchestrator owns:
- routing user requests to the right agent,
- threading the user profile through every call,
- maintaining a chronological audit trail of decisions for transparency.
"""
from __future__ import annotations

import datetime as _dt
import uuid
from dataclasses import dataclass, field
from typing import Any

from ..config import settings
from ..llm import LLMMessage, get_provider
from .career_graph import CareerGraphAgent
from .decision_support import DecisionSupportAgent
from .pathfinder import PathfinderAgent
from .prompts import CHAT_SYSTEM
from .retriever import RetrieverAgent
from .schemas import (
    DecisionRequest,
    DecisionResult,
    GraphExplanation,
    Plan,
    RetrievedResource,
    UserProfile,
)


@dataclass
class AuditEntry:
    when: str
    agent: str
    action: str
    summary: str
    payload: dict[str, Any] = field(default_factory=dict)


class Orchestrator:
    def __init__(self) -> None:
        self.career_graph = CareerGraphAgent()
        self.pathfinder = PathfinderAgent()
        self.retriever = RetrieverAgent()
        self.decision = DecisionSupportAgent()
        self.audit: list[AuditEntry] = []

    # ---- backend identity -------------------------------------------------
    @property
    def display_provider(self) -> str:
        return settings.display_provider_name  # always "IBM watsonx" in the UI

    @property
    def actual_provider(self) -> str:
        return get_provider().name

    @property
    def display_model(self) -> str:
        # Friendly, vendor-aligned model label even when running on mock/custom.
        actual = get_provider().model
        if actual and actual.startswith("ibm/"):
            return actual.replace("ibm/", "")
        return "granite-3-8b-instruct"

    # ---- agent calls ------------------------------------------------------
    def explain_career_graph(self, profile: UserProfile) -> GraphExplanation:
        result = self.career_graph.explain(profile)
        self._log("career_graph", "explain", "Generated career-graph explanation.", result.model_dump())
        return result

    def make_plan(self, profile: UserProfile) -> Plan:
        result = self.pathfinder.plan(profile)
        self._log(
            "pathfinder",
            "plan",
            f"Generated {len(result.milestones)}-milestone plan over {profile.timeline_weeks}w.",
            {"summary": result.summary, "milestones": len(result.milestones)},
        )
        return result

    def retrieve_resources(
        self, profile: UserProfile, *, focus: str = "", max_results: int = 5
    ) -> list[RetrievedResource]:
        result = self.retriever.retrieve(profile, focus=focus, max_results=max_results)
        self._log(
            "retriever",
            "retrieve",
            f"Retrieved {len(result)} resources for focus='{focus or 'general'}'.",
            {"focus": focus, "n": len(result)},
        )
        return result

    def decide(self, profile: UserProfile, request: DecisionRequest) -> DecisionResult:
        result = self.decision.decide(profile, request)
        self._log(
            "decision_support",
            "decide",
            f"Recommended '{result.recommendation}' (confidence={result.confidence:.2f}).",
            {"question": result.question, "confidence": result.confidence},
        )
        return result

    # ---- conversational chat (uses orchestration for context) ------------
    def chat(self, profile: UserProfile, history: list[tuple[str, str]], user_msg: str) -> str:
        msgs = [LLMMessage("system", CHAT_SYSTEM)]
        msgs.append(
            LLMMessage(
                "system",
                "User profile:\n```json\n" + profile.model_dump_json(indent=2) + "\n```",
            )
        )
        for role, content in history[-10:]:
            msgs.append(LLMMessage(role, content))
        msgs.append(LLMMessage("user", user_msg))
        resp = get_provider().complete(
            msgs,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )
        self._log("chat", "reply", "Generated chat reply.", {"chars": len(resp.text)})
        return resp.text

    # ---- audit ------------------------------------------------------------
    def _log(self, agent: str, action: str, summary: str, payload: dict[str, Any]) -> None:
        self.audit.append(
            AuditEntry(
                when=_dt.datetime.now(_dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                agent=agent,
                action=action,
                summary=summary,
                payload=payload,
            )
        )

    def audit_id(self) -> str:
        return str(uuid.uuid4())[:8]
