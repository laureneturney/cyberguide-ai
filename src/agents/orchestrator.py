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
from .profiler import ResumeProfilerAgent
from .prompts import CHAT_SYSTEM
from .retriever import RetrieverAgent
from .schemas import (
    DecisionRequest,
    DecisionResult,
    GraphExplanation,
    Plan,
    ResumeAnalysis,
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
        self.profiler = ResumeProfilerAgent()
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

    def analyze_resume(self, resume_text: str) -> ResumeAnalysis:
        result = self.profiler.analyze(resume_text)
        self._log(
            "resume_profiler",
            "analyze",
            (
                f"Analyzed {len(resume_text or '')}-char resume; "
                f"suggested {result.suggested_role_id or '(none)'} "
                f"in domain {result.suggested_domain_id or '(none)'} "
                f"(confidence={result.confidence:.2f})."
            ),
            {
                "chars": len(resume_text or ""),
                "suggested_domain_id": result.suggested_domain_id,
                "suggested_role_id": result.suggested_role_id,
                "confidence": result.confidence,
            },
        )
        return result

    def apply_resume_to_profile(
        self, base: UserProfile, analysis: ResumeAnalysis
    ) -> UserProfile:
        """Merge analysis fields into a profile without overwriting non-empty user inputs."""
        return base.model_copy(
            update={
                "background": base.background or analysis.background_label,
                "education": base.education or analysis.education,
                "preferred_domain": base.preferred_domain or analysis.suggested_domain_id,
                "target_role": base.target_role or analysis.suggested_role_id,
                "skills_self_rated": {**analysis.skills_detected, **(base.skills_self_rated or {})},
            }
        )

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
