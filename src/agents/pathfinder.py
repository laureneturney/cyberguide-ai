"""Pathfinding agent — produces personalized week-by-week roadmaps."""
from __future__ import annotations

import json

from ..config import settings
from ..data import EVIDENCE_BY_ROLE, role_detail, domain_detail
from ..llm import LLMMessage, get_provider
from .prompts import PATHFINDER_SYSTEM
from .schemas import Milestone, Plan, UserProfile


class PathfinderAgent:
    name = "pathfinder"

    def plan(self, profile: UserProfile) -> Plan:
        role = role_detail(profile.target_role) if profile.target_role else None
        domain = (
            domain_detail(profile.preferred_domain)
            if profile.preferred_domain
            else None
        )
        evidence = EVIDENCE_BY_ROLE.get(profile.target_role, [])

        context = {
            "profile": profile.model_dump(),
            "target_role": role,
            "target_domain": domain,
            "expected_evidence": evidence,
        }
        user = (
            "Personalize a roadmap using ONLY the context below. Stay within "
            "the user's hours and timeline.\n\n```json\n"
            + json.dumps(context, indent=2)
            + "\n```"
        )

        messages = [
            LLMMessage("system", PATHFINDER_SYSTEM),
            LLMMessage("user", user),
        ]
        parsed, _ = get_provider().complete_json(
            messages,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )
        plan_dict = (parsed or {}).get("plan") or _fallback_plan(profile, role, evidence)
        return _coerce_plan(plan_dict)


def _coerce_plan(d: dict) -> Plan:
    milestones = [Milestone(**m) for m in (d.get("milestones") or [])]
    return Plan(
        summary=d.get("summary", ""),
        milestones=milestones,
        risks=list(d.get("risks") or []),
        next_action=d.get("next_action", ""),
        rationale=d.get("rationale", ""),
        generated_with="IBM watsonx",
    )


def _fallback_plan(profile: UserProfile, role, evidence) -> dict:
    weeks = max(4, profile.timeline_weeks or 16)
    hours = profile.weekly_hours or 8
    role_name = (role or {}).get("name", "your target role")
    return {
        "summary": (
            f"A {weeks}-week, {hours}h/week roadmap toward {role_name}, anchored "
            "to public evidence employers can verify."
        ),
        "milestones": [
            {
                "week_range": f"1-{max(2, weeks // 4)}",
                "title": "Foundations & vocabulary",
                "objectives": [
                    "Cover networking, OS, scripting, and cloud-101",
                    "Stand up a simple home lab",
                    "Read the role's job description and translate each line into a skill",
                ],
                "evidence": "Public README of your home-lab setup",
                "rationale": "Without vocabulary fluency you'll bounce off real interviews.",
            },
            {
                "week_range": f"{max(3, weeks // 4 + 1)}-{weeks // 2}",
                "title": "Core skills with proof",
                "objectives": [
                    "Complete a hands-on track aligned to the role",
                    "Publish 2 short write-ups",
                    "Start a study partner / accountability check-in",
                ],
                "evidence": "Two write-ups + one tracked badge",
                "rationale": "Visible artifacts beat invisible coursework every time.",
            },
            {
                "week_range": f"{weeks // 2 + 1}-{int(weeks * 0.75)}",
                "title": "Certify & signal",
                "objectives": [
                    "Earn the role's recruiter-filter cert",
                    "Refactor your résumé and LinkedIn around evidence",
                ],
                "evidence": evidence[0] if evidence else "Earned certification",
                "rationale": "Cert + curated artifacts together pass the ATS gate.",
            },
            {
                "week_range": f"{int(weeks * 0.75) + 1}-{weeks}",
                "title": "Apply, interview, and iterate",
                "objectives": [
                    "5+ targeted applications per week",
                    "1 mock interview per week against role-specific questions",
                ],
                "evidence": "Application + interview log",
                "rationale": "Practice volume beats polish at this stage.",
            },
        ],
        "risks": [
            "Tutorial trap — finish artifacts, don't only watch courses.",
            "Cert-only signal — pair every cert with a public lab artifact.",
        ],
        "next_action": "Open the first milestone and confirm your home-lab stack before week 1.",
    }
