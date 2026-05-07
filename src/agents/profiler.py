"""Resume Profiler agent.

Turns raw resume text (PDF / DOCX / paste) into:
  - a populated UserProfile, and
  - a suggested domain + role grounded in the curated graph.

The agent never fabricates skills, certs, or roles outside the curated graph.
"""
from __future__ import annotations

import json
from typing import Any

from ..config import settings
from ..data import DOMAINS, ROLES
from ..llm import LLMMessage, get_provider
from .prompts import PROFILER_SYSTEM
from .schemas import ResumeAnalysis, UserProfile


# Cap the resume text we send to the model — keeps cost bounded and
# protects against pasted novels.
_MAX_RESUME_CHARS = 12_000


class ResumeProfilerAgent:
    name = "resume_profiler"

    def analyze(self, resume_text: str) -> ResumeAnalysis:
        text = (resume_text or "").strip()[:_MAX_RESUME_CHARS]
        if not text:
            return ResumeAnalysis(
                summary="No resume text provided.",
                background_label="",
                confidence=0.0,
            )

        graph_ctx = {
            "domains": [{"id": d["id"], "name": d["name"]} for d in DOMAINS],
            "roles": [
                {"id": r["id"], "name": r["name"], "domain_id": r["domain_id"], "seniority": r["seniority"]}
                for r in ROLES
            ],
        }
        user = (
            "Resume text:\n```\n" + text + "\n```\n\n"
            "Career graph (you MUST pick suggested_domain_id and suggested_role_id from these):\n"
            "```json\n" + json.dumps(graph_ctx, indent=2) + "\n```"
        )
        messages = [
            LLMMessage("system", PROFILER_SYSTEM),
            LLMMessage("user", user),
        ]
        parsed, _ = get_provider().complete_json(
            messages,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )
        payload = (parsed or {}).get("analysis") or _fallback_analysis(text)
        return _coerce(payload)


# -----------------------------------------------------------------------------
# Coercion + grounding
# -----------------------------------------------------------------------------

_VALID_DOMAINS = {d["id"] for d in DOMAINS}
_VALID_ROLES = {r["id"] for r in ROLES}


def _coerce(d: dict[str, Any]) -> ResumeAnalysis:
    domain_id = str(d.get("suggested_domain_id", "")).strip()
    role_id = str(d.get("suggested_role_id", "")).strip()

    # Drop hallucinated IDs and try to recover from the role's domain mapping.
    if role_id and role_id not in _VALID_ROLES:
        role_id = ""
    if domain_id and domain_id not in _VALID_DOMAINS:
        domain_id = ""
    if role_id and not domain_id:
        for r in ROLES:
            if r["id"] == role_id:
                domain_id = r["domain_id"]
                break

    skills_raw = d.get("skills_detected") or {}
    skills: dict[str, int] = {}
    if isinstance(skills_raw, dict):
        for k, v in skills_raw.items():
            try:
                skills[str(k)] = max(1, min(5, int(v)))
            except (TypeError, ValueError):
                continue

    return ResumeAnalysis(
        summary=str(d.get("summary", "")).strip(),
        background_label=str(d.get("background_label", "")).strip()[:120],
        estimated_years_experience=_safe_float(d.get("estimated_years_experience"), 0.0),
        education=str(d.get("education", "")).strip(),
        skills_detected=skills,
        certifications=[str(c).strip() for c in (d.get("certifications") or []) if str(c).strip()],
        courses=[str(c).strip() for c in (d.get("courses") or []) if str(c).strip()],
        suggested_domain_id=domain_id,
        suggested_role_id=role_id,
        rationale=str(d.get("rationale", "")).strip(),
        gaps_for_target=[str(g).strip() for g in (d.get("gaps_for_target") or []) if str(g).strip()],
        confidence=_safe_float(d.get("confidence"), 0.5, lo=0.0, hi=1.0),
    )


def _safe_float(value: Any, default: float, *, lo: float | None = None, hi: float | None = None) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        v = default
    if lo is not None:
        v = max(lo, v)
    if hi is not None:
        v = min(hi, v)
    return v


# -----------------------------------------------------------------------------
# Heuristic fallback (used when the LLM returns nothing parseable)
# -----------------------------------------------------------------------------

_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "soc": ["soc", "siem", "splunk", "sentinel", "edr", "incident", "alert", "triage"],
    "grc": ["grc", "compliance", "risk", "audit", "soc 2", "iso 27001", "nist", "policy"],
    "appsec": ["appsec", "application security", "owasp", "sast", "dast", "secure code"],
    "offensive": ["pentest", "penetration", "red team", "exploit", "burp", "ctf"],
    "cloud": ["aws", "azure", "gcp", "kubernetes", "terraform", "iam policy"],
    "iam": ["iam", "okta", "entra", "saml", "oidc", "sso", "mfa"],
    "dfir": ["forensics", "dfir", "memory analysis", "incident response", "volatility"],
    "engineering": ["python", "go", "infrastructure", "devops", "ci/cd", "automation"],
}


def _fallback_analysis(text: str) -> dict[str, Any]:
    lowered = text.lower()
    scored = {
        domain_id: sum(1 for kw in keywords if kw in lowered)
        for domain_id, keywords in _DOMAIN_KEYWORDS.items()
    }
    domain_id = max(scored, key=scored.get) if any(scored.values()) else "soc"
    role_id = next((r["id"] for r in ROLES if r["domain_id"] == domain_id and r["seniority"] == "entry"),
                   "soc_t1")

    skills: dict[str, int] = {}
    for label in ("Networking", "Linux", "Windows", "Python", "Cloud (AWS/Azure/GCP)"):
        if label.split()[0].lower() in lowered:
            skills[label] = 3

    return {
        "summary": "Heuristic extraction (LLM unavailable). Confidence is low.",
        "background_label": "Career changer / early professional",
        "estimated_years_experience": 1.0,
        "education": "",
        "skills_detected": skills,
        "certifications": [],
        "courses": [],
        "suggested_domain_id": domain_id,
        "suggested_role_id": role_id,
        "rationale": "Picked the domain with the most keyword overlap in your resume.",
        "gaps_for_target": ["Detailed evidence of role-specific projects"],
        "confidence": 0.4,
    }
