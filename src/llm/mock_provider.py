"""Deterministic mock provider for offline demos and Streamlit Cloud previews.

The mock parses lightweight intent tags from the system prompt (the orchestrator
adds them) so each agent gets a sensible canned response without ever calling
out to the network. It's good enough to demonstrate the full UX — branching
plans, retrieved resources, decision trade-offs, chat — with zero secrets.
"""
from __future__ import annotations

import json
import random
import re
from typing import Any

from .base import LLMMessage, LLMProvider, LLMResponse


_INTENT_TAG = re.compile(r"<INTENT:([A-Z_]+)>")


class MockLLM(LLMProvider):
    name = "mock"
    model = "cyberguide-mock-v1"

    def __init__(self, seed: int = 7) -> None:
        self._rng = random.Random(seed)

    def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.3,
        max_tokens: int = 800,
    ) -> LLMResponse:
        intent = self._extract_intent(messages)
        user_block = "\n".join(m.content for m in messages if m.role == "user")
        profile = _try_extract_json_block(user_block, key="profile") or {}
        text = _DISPATCH.get(intent, _generic_chat)(profile, user_block, self._rng)
        return LLMResponse(text=text, provider=self.name, model=self.model, usage=None)

    @staticmethod
    def _extract_intent(messages: list[LLMMessage]) -> str:
        for m in messages:
            match = _INTENT_TAG.search(m.content or "")
            if match:
                return match.group(1)
        return "CHAT"


def _try_extract_json_block(text: str, *, key: str | None = None) -> dict | None:
    if not text:
        return None
    pattern = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)
    m = pattern.search(text)
    raw = m.group(1) if m else None
    if raw is None:
        # try fenceless
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            raw = text[start : end + 1]
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except Exception:
        return None
    if key and isinstance(data, dict) and key in data and isinstance(data[key], dict):
        return data[key]
    return data if isinstance(data, dict) else None


def _user_summary(profile: dict) -> dict:
    return {
        "name": profile.get("name") or "there",
        "background": profile.get("background") or "general professional",
        "domain": profile.get("preferred_domain") or "Security Operations (SOC)",
        "role": profile.get("target_role") or "SOC Analyst (Tier 1)",
        "hours": profile.get("weekly_hours", 8),
        "weeks": profile.get("timeline_weeks", 16),
        "constraints": profile.get("constraints") or "limited budget; self-paced",
    }


def _pathfinder(profile: dict, user: str, rng: random.Random) -> str:
    s = _user_summary(profile)
    plan = {
        "summary": (
            f"A {s['weeks']}-week, {s['hours']}h/week roadmap from "
            f"\"{s['background']}\" toward {s['role']} in the {s['domain']} domain."
        ),
        "milestones": [
            {
                "week_range": "1-3",
                "title": "Foundations & vocabulary",
                "objectives": [
                    "Complete CompTIA Security+ domain 1 & 2 (threats, architecture)",
                    "Set up a home lab: pfSense + 2 VMs (attacker + victim)",
                    "Read the MITRE ATT&CK overview; map 5 techniques to real-world incidents",
                ],
                "evidence": "Lab repo on GitHub with README + screenshots",
                "rationale": "Employers screen for vocabulary fluency before depth.",
            },
            {
                "week_range": "4-7",
                "title": "Detection & triage core skills",
                "objectives": [
                    "Practice 30+ TryHackMe SOC-tier rooms",
                    "Build a Splunk or Wazuh dashboard for a Sysmon-instrumented host",
                    "Write 3 incident reports from BlueTeamLabs scenarios",
                ],
                "evidence": "Public dashboards + 3 short incident write-ups on a blog",
                "rationale": "Tier-1 SOC interviews ask 'walk me through a triage' — this is your answer.",
            },
            {
                "week_range": "8-12",
                "title": "Certify and signal",
                "objectives": [
                    "Pass CompTIA Security+ (SY0-701)",
                    "Earn TryHackMe SOC Level 1 path completion",
                    "Refactor LinkedIn + résumé to surface lab evidence",
                ],
                "evidence": "Sec+ digital badge + SOC L1 certificate + updated profile",
                "rationale": "These are the two recruiter filters that get you past the ATS.",
            },
            {
                "week_range": "13-16",
                "title": "Apply & interview",
                "objectives": [
                    "Apply to 5 roles per week, focused on MSSPs and mid-market SOCs",
                    "Mock interview weekly using the BTL1 scenario bank",
                    "Network: 2 informational chats per week",
                ],
                "evidence": "Interview log + offer pipeline tracker",
                "rationale": "Practice volume beats polish here.",
            },
        ],
        "risks": [
            "Tutorial trap — finish projects, don't just watch courses.",
            "Cert-only signal — without lab artifacts, certs alone underperform.",
        ],
        "next_action": "Open the home-lab milestone and confirm your VM stack before week 1.",
    }
    return "```json\n" + json.dumps({"plan": plan}, indent=2) + "\n```"


def _retriever(profile: dict, user: str, rng: random.Random) -> str:
    s = _user_summary(profile)
    items = [
        {
            "title": "TryHackMe — SOC Level 1 Path",
            "kind": "lab",
            "url": "https://tryhackme.com/path/outline/soclevel1",
            "why": f"Hands-on triage practice tuned to {s['role']} interviews.",
            "cost": "$14/mo",
            "time_estimate": "60–90 hrs",
        },
        {
            "title": "CompTIA Security+ (SY0-701) — Official Study Guide",
            "kind": "certification",
            "url": "https://www.comptia.org/certifications/security",
            "why": "Most-asked-for entry-level cert by US recruiters.",
            "cost": "$392 exam",
            "time_estimate": "8–12 weeks",
        },
        {
            "title": "Blue Team Labs Online — Investigations",
            "kind": "lab",
            "url": "https://blueteamlabs.online/",
            "why": "Realistic SOC scenarios with reportable evidence.",
            "cost": "Free + paid tiers",
            "time_estimate": "self-paced",
        },
        {
            "title": "MITRE ATT&CK Navigator",
            "kind": "reference",
            "url": "https://mitre-attack.github.io/attack-navigator/",
            "why": "The shared vocabulary every SOC interview leans on.",
            "cost": "Free",
            "time_estimate": "ongoing",
        },
        {
            "title": "Cyber Defenders — Blue Team CTFs",
            "kind": "lab",
            "url": "https://cyberdefenders.org/",
            "why": "DFIR-flavored challenges to round out detection skills.",
            "cost": "Free + paid",
            "time_estimate": "self-paced",
        },
    ]
    rng.shuffle(items)
    return "```json\n" + json.dumps({"resources": items[:5]}, indent=2) + "\n```"


def _decision_support(profile: dict, user: str, rng: random.Random) -> str:
    decision = {
        "question": "Should you target SOC Analyst or jump straight to Security Engineer?",
        "options": [
            {
                "label": "SOC Analyst (Tier 1)",
                "pros": [
                    "Lowest barrier to first cyber job",
                    "Exposure to wide range of incidents",
                    "Well-defined skill ramp",
                ],
                "cons": [
                    "Shift work / on-call common",
                    "Slower comp curve early",
                ],
                "fit_score": 0.82,
            },
            {
                "label": "Security Engineer (Junior)",
                "pros": [
                    "Higher ceiling and comp",
                    "Plays to your existing engineering background",
                ],
                "cons": [
                    "Few true junior openings",
                    "Requires a stronger portfolio than a typical newcomer has",
                ],
                "fit_score": 0.61,
            },
        ],
        "recommendation": "SOC Analyst (Tier 1)",
        "rationale": (
            "Given your timeline, evidence base, and goal of a first cyber role within "
            "16 weeks, SOC offers the highest probability of an offer while still "
            "feeding a Security Engineer pivot in 18–24 months."
        ),
        "confidence": 0.78,
        "human_review_required": True,
    }
    return "```json\n" + json.dumps({"decision": decision}, indent=2) + "\n```"


def _career_graph(profile: dict, user: str, rng: random.Random) -> str:
    explanation = {
        "domain_overview": (
            "Security Operations (SOC) is the detection-and-response heart of most "
            "security programs. It's where alerts land, get triaged, and become "
            "incidents. Roles here split into monitoring (Tier 1/2 analysts), "
            "investigation (DFIR), and engineering (detection engineers)."
        ),
        "key_roles": [
            "SOC Analyst (Tier 1)",
            "SOC Analyst (Tier 2)",
            "Detection Engineer",
            "Incident Responder",
        ],
        "core_skills": [
            "Log analysis (Splunk / ELK / Sentinel)",
            "Endpoint telemetry (EDR, Sysmon)",
            "Network basics (TCP/IP, DNS, HTTP)",
            "MITRE ATT&CK mapping",
            "Triage & incident write-ups",
        ],
        "evidence_employers_value": [
            "Public lab walkthroughs (GitHub / blog)",
            "TryHackMe / BTL1 / CyberDefenders badges",
            "CompTIA Security+ or BTL1 certification",
            "A short incident-report writing sample",
        ],
        "common_first_role": "SOC Analyst (Tier 1) at an MSSP or mid-market in-house SOC.",
    }
    return "```json\n" + json.dumps({"graph_explanation": explanation}, indent=2) + "\n```"


def _generic_chat(profile: dict, user: str, rng: random.Random) -> str:
    s = _user_summary(profile)
    return (
        f"Here's a CyberGuide answer tailored to a {s['domain']} path toward {s['role']}.\n\n"
        "• Anchor every week to one piece of public evidence (lab, write-up, badge).\n"
        "• Treat certifications as recruiter filters, not learning vehicles.\n"
        "• Re-plan when your hours, target role, or constraints shift — don't grind through a stale plan.\n\n"
        "Tell me what you'd like to drill into next: a specific role, a decision, or a resource."
    )


def _profiler(profile: dict, user: str, rng: random.Random) -> str:
    # Lightweight keyword scan against the resume text included in the user
    # block. The real LLM will do better — this is just a sane offline default.
    text = (user or "").lower()

    keyword_map = {
        "soc": ["soc", "siem", "splunk", "sentinel", "edr", "incident", "alert", "triage"],
        "grc": ["grc", "compliance", "risk", "audit", "soc 2", "iso 27001", "nist", "policy"],
        "appsec": ["appsec", "application security", "owasp", "sast", "dast"],
        "offensive": ["pentest", "penetration", "red team", "exploit", "burp", "ctf"],
        "cloud": ["aws", "azure", "gcp", "kubernetes", "terraform"],
        "iam": ["iam", "okta", "entra", "saml", "oidc", "sso", "mfa"],
        "dfir": ["forensics", "dfir", "memory analysis", "volatility"],
        "engineering": ["python", "go ", "devops", "ci/cd", "automation"],
    }
    scores = {dom: sum(1 for kw in kws if kw in text) for dom, kws in keyword_map.items()}
    domain_id = max(scores, key=scores.get) if any(scores.values()) else "soc"
    role_map = {
        "soc": "soc_t1", "grc": "grc_analyst", "appsec": "appsec_eng",
        "offensive": "pentester", "cloud": "cloudsec_eng", "iam": "iam_eng",
        "dfir": "forensics", "engineering": "junior_sec_eng",
    }
    role_id = role_map.get(domain_id, "soc_t1")

    skills: dict[str, int] = {}
    skill_hints = [
        ("Networking", ["tcp", "dns", "vpn", "firewall", "wireshark", "network"]),
        ("Linux", ["linux", "bash", "ubuntu", "centos", "shell"]),
        ("Windows", ["windows", "active directory", "powershell"]),
        ("Scripting (Python or PowerShell)", ["python", "powershell", "bash script"]),
        ("Cloud (AWS/Azure/GCP)", ["aws", "azure", "gcp"]),
        ("Security tooling (SIEM/EDR)", ["splunk", "sentinel", "crowdstrike", "edr", "siem"]),
    ]
    for label, kws in skill_hints:
        hits = sum(1 for k in kws if k in text)
        if hits:
            skills[label] = min(5, 2 + hits)

    cert_hints = ["security+", "cysa+", "ccna", "aws certified", "ceh", "oscp", "pnpt", "sc-900", "isc2 cc"]
    certs = [c for c in cert_hints if c in text]

    analysis = {
        "summary": (
            "Candidate looks like a strong fit for an entry path in cybersecurity, "
            "with transferable evidence and at least one role-relevant signal."
        ),
        "background_label": "Career changer with adjacent technical exposure",
        "estimated_years_experience": 2.0,
        "education": "Inferred from resume",
        "skills_detected": skills or {"Networking": 2, "Linux": 2},
        "certifications": [c.title() for c in certs],
        "courses": [],
        "suggested_domain_id": domain_id,
        "suggested_role_id": role_id,
        "rationale": (
            f"Resume keywords align most strongly with the {domain_id.upper()} domain. "
            "The recommended role is the most common entry point in that domain."
        ),
        "gaps_for_target": [
            "Public lab artifact (write-up + repo)",
            "Recruiter-filter certification",
        ],
        "confidence": 0.7 if any(scores.values()) else 0.45,
    }
    return "```json\n" + json.dumps({"analysis": analysis}, indent=2) + "\n```"


_DISPATCH: dict[str, Any] = {
    "PATHFINDER": _pathfinder,
    "RETRIEVER": _retriever,
    "DECISION": _decision_support,
    "CAREER_GRAPH": _career_graph,
    "PROFILER": _profiler,
    "CHAT": _generic_chat,
}
