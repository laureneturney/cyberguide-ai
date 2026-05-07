"""Career Navigation Graph agent.

Owns the structured map of domains → roles → skills → evidence and produces
LLM-augmented explanations grounded in that map.
"""
from __future__ import annotations

import json

from ..data import (
    DOMAINS,
    EVIDENCE_BY_ROLE,
    ROLES,
    SKILL_GROUPS,
    domain_detail,
    role_detail,
)
from ..llm import LLMMessage, get_provider
from ..config import settings
from .prompts import CAREER_GRAPH_SYSTEM
from .schemas import GraphExplanation, UserProfile


class CareerGraphAgent:
    name = "career_graph"

    def explain(self, profile: UserProfile) -> GraphExplanation:
        domain_id = profile.preferred_domain or "soc"
        role_id = profile.target_role or _default_role_for(domain_id)
        domain = domain_detail(domain_id) or DOMAINS[0]
        role = role_detail(role_id)

        related_roles = [
            r["name"] for r in ROLES if r["domain_id"] == domain["id"]
        ][:6]
        skills_pool = sum(SKILL_GROUPS.values(), [])
        evidence = EVIDENCE_BY_ROLE.get(role_id, [])

        context = {
            "profile": profile.model_dump(),
            "domain": domain,
            "role": role,
            "domain_roles": related_roles,
            "skill_pool_sample": skills_pool[:14],
            "evidence_samples": evidence,
        }
        user = (
            "Use ONLY the data below. Produce the JSON described in the system prompt.\n\n"
            "```json\n" + json.dumps(context, indent=2) + "\n```"
        )

        messages = [
            LLMMessage("system", CAREER_GRAPH_SYSTEM),
            LLMMessage("user", user),
        ]
        parsed, _ = get_provider().complete_json(
            messages,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )
        payload = (parsed or {}).get("graph_explanation") or _fallback_explanation(
            domain, role, related_roles, evidence
        )
        return GraphExplanation(**payload)


def _default_role_for(domain_id: str) -> str:
    for r in ROLES:
        if r["domain_id"] == domain_id and r["seniority"] == "entry":
            return r["id"]
    for r in ROLES:
        if r["domain_id"] == domain_id:
            return r["id"]
    return "soc_t1"


def _fallback_explanation(domain, role, related_roles, evidence) -> dict:
    return {
        "domain_overview": (
            f"{domain['name']} — {domain['blurb']} It is one of the highest-volume entry "
            f"points into cybersecurity, with clear feeder roles and a defined skill ramp."
        ),
        "key_roles": related_roles,
        "core_skills": (role or {}).get("core_skills", [])
        or ["Networking", "Operating systems", "Scripting", "Cloud literacy"],
        "evidence_employers_value": evidence
        or ["Public lab walkthroughs", "Entry-level certifications", "Short incident write-ups"],
        "common_first_role": (role or {}).get("name", "SOC Analyst (Tier 1)"),
    }
