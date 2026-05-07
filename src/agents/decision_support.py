"""Decision support agent.

Helps users navigate the forks where most newcomers stall — picking a
domain, choosing a first cert, deciding between SOC vs. AppSec, etc.
Always returns a structured trade-off plus a recommendation gated on
human review.
"""
from __future__ import annotations

import json

from ..config import settings
from ..llm import LLMMessage, get_provider
from .prompts import DECISION_SYSTEM
from .schemas import DecisionOption, DecisionRequest, DecisionResult, UserProfile


class DecisionSupportAgent:
    name = "decision_support"

    def decide(self, profile: UserProfile, request: DecisionRequest) -> DecisionResult:
        context = {
            "profile": profile.model_dump(),
            "request": request.model_dump(),
        }
        user = (
            "Produce the JSON described in the system prompt. Honor the user's "
            "stated constraints; rationalize against the user's profile.\n\n"
            "```json\n" + json.dumps(context, indent=2) + "\n```"
        )
        messages = [
            LLMMessage("system", DECISION_SYSTEM),
            LLMMessage("user", user),
        ]
        parsed, _ = get_provider().complete_json(
            messages,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )
        d = (parsed or {}).get("decision") or _fallback_decision(request)
        return _coerce_decision(d, request)


def _coerce_decision(d: dict, fallback_req: DecisionRequest) -> DecisionResult:
    options_raw = d.get("options") or []
    options = []
    for o in options_raw:
        if not isinstance(o, dict):
            continue
        options.append(
            DecisionOption(
                label=str(o.get("label", "")).strip() or "Option",
                pros=list(o.get("pros") or []),
                cons=list(o.get("cons") or []),
                fit_score=_clamp(float(o.get("fit_score", 0.5))),
            )
        )
    if not options:
        options = [DecisionOption(label=opt) for opt in fallback_req.options or ["Option A", "Option B"]]

    rec = str(d.get("recommendation", "")).strip() or options[0].label
    if rec not in {o.label for o in options}:
        rec = options[0].label
    return DecisionResult(
        question=str(d.get("question") or fallback_req.question or "Decision"),
        options=options,
        recommendation=rec,
        rationale=str(d.get("rationale", "")).strip(),
        confidence=_clamp(float(d.get("confidence", 0.6))),
        human_review_required=True,
    )


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        return max(lo, min(hi, x))
    except Exception:
        return 0.5


def _fallback_decision(request: DecisionRequest) -> dict:
    options = request.options or ["Option A", "Option B"]
    return {
        "question": request.question or "Which path should I take?",
        "options": [
            {
                "label": options[0],
                "pros": ["Lower barrier to start"],
                "cons": ["May limit ceiling near-term"],
                "fit_score": 0.6,
            },
            {
                "label": options[1] if len(options) > 1 else "Alternative",
                "pros": ["Higher ceiling"],
                "cons": ["Steeper ramp before first offer"],
                "fit_score": 0.5,
            },
        ],
        "recommendation": options[0],
        "rationale": (
            "Without a more detailed profile we recommend the lower-barrier option "
            "and revisit in 8 weeks."
        ),
        "confidence": 0.55,
        "human_review_required": True,
    }
