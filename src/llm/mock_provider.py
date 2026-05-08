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
    role_id = profile.get("target_role") or "soc_t1"
    domain_id = profile.get("preferred_domain") or "soc"
    return {
        "name": (profile.get("name") or "").strip() or "you",
        "background": profile.get("background") or "general professional",
        "domain_id": domain_id,
        "role_id": role_id,
        "domain_name": _DOMAIN_NAMES.get(domain_id, "Security Operations (SOC)"),
        "role_name": _ROLE_NAMES.get(role_id, "SOC Analyst (Tier 1)"),
        "hours": int(profile.get("weekly_hours") or 8),
        "weeks": int(profile.get("timeline_weeks") or 16),
        "budget": int(profile.get("budget_usd") or 0),
        "constraints": (profile.get("constraints") or "").strip(),
        "skills": profile.get("skills_self_rated") or {},
        "education": (profile.get("education") or "").strip(),
        "interests": profile.get("interests") or [],
    }


# Friendly names for IDs — kept tiny and self-contained so the mock has zero
# imports from the data package (avoids a circular-ish dependency).
_DOMAIN_NAMES = {
    "soc": "Security Operations (SOC)",
    "grc": "Governance, Risk & Compliance",
    "appsec": "Application Security",
    "offensive": "Offensive Security",
    "cloud": "Cloud Security",
    "iam": "Identity & Access Management",
    "dfir": "Digital Forensics & Incident Response",
    "engineering": "Security Engineering",
}
_ROLE_NAMES = {
    "soc_t1": "SOC Analyst (Tier 1)", "soc_t2": "SOC Analyst (Tier 2)",
    "detection_eng": "Detection Engineer", "ir": "Incident Responder",
    "forensics": "Digital Forensics Analyst", "grc_analyst": "GRC Analyst",
    "compliance_mgr": "Compliance Manager", "appsec_eng": "Application Security Engineer",
    "pentester": "Penetration Tester", "red_teamer": "Red Team Operator",
    "cloudsec_eng": "Cloud Security Engineer", "iam_eng": "IAM Engineer",
    "sec_eng": "Security Engineer (Generalist)", "junior_sec_eng": "Junior Security Engineer",
}


# Per-role objective templates. Each role gets its own foundation focus, core
# skill set, recruiter-filter cert, employer targets, and risks. The mock
# pathfinder weaves these into milestones tuned to the user's hours / weeks /
# budget / skill levels.
_ROLE_PLAYBOOKS: dict[str, dict[str, Any]] = {
    "soc_t1": {
        "core_title": "Detection & triage core skills",
        "core_objectives": [
            "Run 25+ TryHackMe SOC-tier rooms; publish a write-up after every 5",
            "Build a Splunk or Wazuh dashboard against a Sysmon-instrumented host",
            "Author 3 incident reports from Blue Team Labs scenarios",
        ],
        "core_evidence": "Public dashboard repo + 3 incident write-ups on a personal blog",
        "core_rationale": "Tier-1 interviews ask 'walk me through a triage' — these artifacts ARE your answer.",
        "cert_name": "CompTIA Security+", "cert_cost": "$392",
        "employer_targets": "MSSPs, mid-market in-house SOCs, and managed-detection providers",
        "first_action": "Stand up your home-lab VM stack (Sysmon + Splunk free) before Week 1 ends.",
        "base_risks": [
            "Tutorial trap — finish artifacts, don't only watch courses.",
            "Cert-only signal — Sec+ alone underperforms without lab evidence.",
        ],
    },
    "soc_t2": {
        "core_title": "Threat hunting & detection authoring",
        "core_objectives": [
            "Hunt across a public dataset (Mordor / CASCADE) with 3 documented hypotheses",
            "Author 5 Sigma rules with explicit test cases",
            "Mentor a Tier-1 study partner; document the mentorship in writing",
        ],
        "core_evidence": "GitHub repo of Sigma rules + a hunt write-up",
        "core_rationale": "Tier-2 hires are judged on detection authorship and mentoring instinct.",
        "cert_name": "BTL1 (Blue Team Level 1)", "cert_cost": "$499",
        "employer_targets": "enterprise SOCs and detection-engineering teams",
        "first_action": "Pick a hunt hypothesis this week and outline the data sources you'd need.",
        "base_risks": [
            "Skipping the writing — detection engineering is judged on clarity, not volume.",
        ],
    },
    "detection_eng": {
        "core_title": "Detection-as-code in public",
        "core_objectives": [
            "Open-source 5 Sigma rules with CI tests on GitHub Actions",
            "Write a blog post describing your detection-engineering methodology",
            "Refactor one rule end-to-end based on community feedback",
        ],
        "core_evidence": "Public Sigma repo with passing CI + 1 published methodology post",
        "core_rationale": "Detection-engineering hires are made from public artifacts, almost without exception.",
        "cert_name": "GIAC GCDA (or BTL1 as a precursor)", "cert_cost": "$2,499 (GCDA)",
        "employer_targets": "tech companies and mature enterprise SOCs",
        "first_action": "Fork SigmaHQ/sigma and ship a draft rule by end of week 1.",
        "base_risks": [
            "Spending too long on the perfect rule — ship rough, iterate in public.",
        ],
    },
    "ir": {
        "core_title": "Hands-on incident response",
        "core_objectives": [
            "Complete 4 BTL Investigations end-to-end with public write-ups",
            "Practice memory forensics with Volatility on 3 sample images",
            "Run a mock IR tabletop with a study partner",
        ],
        "core_evidence": "BTL badge + memory-forensics walkthrough on a blog",
        "core_rationale": "IR is judged on calmness under pressure; tabletops are how you signal it.",
        "cert_name": "GCIH (or BTL1 first)", "cert_cost": "$2,499 (GCIH)",
        "employer_targets": "IR consultancies (Mandiant, CrowdStrike, Unit 42) and large enterprises",
        "first_action": "Set up a Volatility-ready VM and grab a sample memory image this week.",
        "base_risks": ["Underestimating writing — IR reports are the deliverable."],
    },
    "forensics": {
        "core_title": "Disk + memory forensics fluency",
        "core_objectives": [
            "Solve 5 CyberDefenders DFIR challenges with public reports",
            "Practice chain-of-custody documentation against a sample case",
            "Build a personal Autopsy + Volatility cheat sheet",
        ],
        "core_evidence": "Public CyberDefenders write-ups + cheat sheet repo",
        "core_rationale": "Forensics interviews probe written communication as much as tools.",
        "cert_name": "GCFE (or AWS Certified Forensics)", "cert_cost": "$2,499",
        "employer_targets": "law-firm consultancies, government, and DFIR specialists",
        "first_action": "Pick a CyberDefenders challenge and timebox it to 6 hours this week.",
        "base_risks": ["Skipping the report — every challenge gets a write-up."],
    },
    "grc_analyst": {
        "core_title": "Map controls to a real framework",
        "core_objectives": [
            "Complete a mock SOC 2 readiness assessment for a fictional SaaS",
            "Build a 15-line risk register with mitigations and owners",
            "Write a 2-page summary tying NIST CSF subcategories to controls",
        ],
        "core_evidence": "Mock SOC 2 readiness pack + risk register + framework write-up",
        "core_rationale": "GRC interviewers want to see writing, not buzzwords.",
        "cert_name": "ISC2 Certified in Cybersecurity (CC)", "cert_cost": "Free",
        "employer_targets": "SaaS, fintech, healthcare, and consulting",
        "first_action": "Pick a fictional SaaS product and outline its 5 most critical controls.",
        "base_risks": [
            "Resisting evidence work because it 'isn't technical' — it is, and it's the differentiator.",
        ],
    },
    "compliance_mgr": {
        "core_title": "Run a mini external audit cycle",
        "core_objectives": [
            "Author a vendor-risk program write-up against ISO 27001 Annex A",
            "Build a 30-control crosswalk between SOC 2 and NIST CSF",
            "Practice a stakeholder briefing on a hypothetical finding",
        ],
        "core_evidence": "Crosswalk + vendor-risk write-up published to your portfolio",
        "core_rationale": "Compliance leaders are hired on authored documents and stakeholder posture.",
        "cert_name": "CISA (Certified Information Systems Auditor)", "cert_cost": "$760",
        "employer_targets": "public companies and regulated industries",
        "first_action": "Sketch the crosswalk skeleton and pick the first 5 controls to map.",
        "base_risks": ["Not treating writing as the deliverable; auditors live in documents."],
    },
    "appsec_eng": {
        "core_title": "Threat-model + secure-code in the open",
        "core_objectives": [
            "Threat-model an open-source app you use; publish the document",
            "Solve 20 PortSwigger Web Security Academy labs",
            "Submit at least 1 sanitized bug-bounty write-up or patch",
        ],
        "core_evidence": "Threat-model doc + Web Security Academy badge + 1 disclosure",
        "core_rationale": "AppSec hires are made on threat models more than vulnerabilities found.",
        "cert_name": "OSWE (advanced) — start with PortSwigger free", "cert_cost": "$1,749 (OSWE)",
        "employer_targets": "tech, fintech, and product companies",
        "first_action": "Pick the open-source app to threat-model and clone the repo this week.",
        "base_risks": [
            "Going deep on exploits without practicing reviews — interviews probe both.",
        ],
    },
    "pentester": {
        "core_title": "CTF cadence + report writing",
        "core_objectives": [
            "Solve 10 Hack The Box machines (mix easy/medium) with public write-ups",
            "Practice a sanitized pentest report against a retired box",
            "Build an Active Directory home lab and exploit it twice",
        ],
        "core_evidence": "Public CTF write-ups + sanitized pentest report PDF",
        "core_rationale": "Pentest hiring is gated on the report — not the shells.",
        "cert_name": "PNPT (or OSCP if budget allows)", "cert_cost": "$399 (PNPT)",
        "employer_targets": "consulting firms and internal red teams",
        "first_action": "Pick the first easy HTB machine and timebox it to 4 hours.",
        "base_risks": [
            "Walking past the report writing — the report IS the product.",
        ],
    },
    "red_teamer": {
        "core_title": "Long-running emulation work",
        "core_objectives": [
            "Build a custom C2 redirector lab with documented OPSEC choices",
            "Develop one TTP (e.g., novel persistence) and detect it yourself",
            "Submit a CFP draft for a defensive-aware red team talk",
        ],
        "core_evidence": "Lab repo + a published TTP detect-and-evade write-up",
        "core_rationale": "Red team hires are gated on TTP development and OPSEC.",
        "cert_name": "CRTO (Certified Red Team Operator)", "cert_cost": "£365",
        "employer_targets": "FAANG, defense contractors, and specialist consultancies",
        "first_action": "Sketch your lab topology and pick the C2 framework you'll start with.",
        "base_risks": ["Optimizing for tools over methodology; methodology wins interviews."],
    },
    "cloudsec_eng": {
        "core_title": "Hardened reference cloud environment",
        "core_objectives": [
            "Build a Terraform repo for an AWS multi-account guardrail baseline",
            "Run a CSPM (Prowler / Steampipe) and document 5 fixes",
            "Threat-model a Kubernetes cluster — pod, network, and identity layers",
        ],
        "core_evidence": "Terraform repo + CSPM remediation diary + a cluster threat model",
        "core_rationale": "Cloud security interviews probe IaC and identity above all else.",
        "cert_name": "AWS Security Specialty (or AZ-500 for Azure shops)", "cert_cost": "$300",
        "employer_targets": "cloud-native companies and enterprises mid-migration",
        "first_action": "Stand up a free-tier AWS account and a Terraform skeleton this week.",
        "base_risks": ["Memorizing services — interviewers want trade-offs and IAM nuance."],
    },
    "iam_eng": {
        "core_title": "Build a working identity stack",
        "core_objectives": [
            "Stand up an Okta or Entra demo tenant with SSO + lifecycle automation",
            "Author a zero-trust architecture diagram with rationale",
            "Practice IAM-policy code reviews in writing",
        ],
        "core_evidence": "Demo tenant export + ZTNA architecture document",
        "core_rationale": "IAM hires are made from architecture writing and SAML/OIDC fluency.",
        "cert_name": "Microsoft SC-300 (or Okta Certified Professional)", "cert_cost": "$165 (SC-300)",
        "employer_targets": "mid-to-large enterprises and identity-heavy SaaS",
        "first_action": "Get an Okta developer or Entra tenant provisioned this week.",
        "base_risks": ["Skipping protocol depth — SAML/OIDC questions filter candidates."],
    },
    "sec_eng": {
        "core_title": "Detection-as-code + tooling",
        "core_objectives": [
            "Open-source a small security tool (linter / pre-commit hook / IaC scanner)",
            "Build a CI pipeline for detection content with passing tests",
            "Write a system-design post (e.g., 'designing our secrets pipeline')",
        ],
        "core_evidence": "Public tool repo + CI badge + system-design post",
        "core_rationale": "Security engineers are hired on engineering rigor first, security depth second.",
        "cert_name": "AWS Security Specialty (or none — show code)", "cert_cost": "$300",
        "employer_targets": "tech companies and scale-ups",
        "first_action": "Pick the small tool and write its README before any code.",
        "base_risks": ["Confusing 'security knowledge' with 'security engineering' — they reward different work."],
    },
    "junior_sec_eng": {
        "core_title": "Engineering portfolio with a security flavor",
        "core_objectives": [
            "Build a small security side project (mini SAST tool or log parser)",
            "Contribute 1 open-source PR to a security-adjacent repo",
            "Set up an AWS Cloud Practitioner-level free-tier sandbox",
        ],
        "core_evidence": "Side-project repo + merged PR + AWS sandbox documentation",
        "core_rationale": "Junior security-engineer roles index hard on demonstrated engineering taste.",
        "cert_name": "ISC2 CC + AWS Cloud Practitioner", "cert_cost": "Free + $100",
        "employer_targets": "tech-forward companies with apprenticeship tracks",
        "first_action": "Pick the side project and open the empty GitHub repo this week.",
        "base_risks": ["Hiding behind certs — engineering managers want to read your code."],
    },
}


def _pathfinder(profile: dict, user: str, rng: random.Random) -> str:
    s = _user_summary(profile)
    weeks = max(4, s["weeks"])
    hours = max(2, s["hours"])
    budget = s["budget"]
    constraints = (s["constraints"] or "").lower()
    skills = s["skills"] or {}
    avg_skill = (sum(skills.values()) / len(skills)) if skills else 1.0
    has_foundation = avg_skill >= 3.5

    book = _ROLE_PLAYBOOKS.get(s["role_id"], _ROLE_PLAYBOOKS["soc_t1"])

    # Phase boundaries proportional to the user's actual timeline.
    p1_end = max(2, weeks // 4)
    p2_end = max(p1_end + 1, weeks // 2)
    p3_end = max(p2_end + 1, int(weeks * 0.75))
    p4_end = weeks

    milestones: list[dict[str, Any]] = []

    # Phase 1: foundations — only if skills suggest it's needed.
    if not has_foundation:
        foundation_focus = {
            "soc": "networking, Linux/Windows, and ATT&CK vocabulary",
            "grc": "NIST CSF and SOC 2 fundamentals",
            "appsec": "OWASP Top 10 and reading code defensively",
            "offensive": "networking, Linux, and an intro to web exploitation",
            "cloud": "AWS or Azure 101 plus IAM basics",
            "iam": "SAML/OIDC fundamentals and directory concepts",
            "dfir": "Linux/Windows internals and disk/memory basics",
            "engineering": "Python or Go, Linux, and CI/CD basics",
        }.get(s["domain_id"], "networking, Linux/Windows, and security vocabulary")
        milestones.append({
            "week_range": f"1-{p1_end}",
            "title": f"Foundations — {foundation_focus}",
            "objectives": [
                f"Cover {foundation_focus} at {hours}h/week",
                "Stand up a small home lab so you can experiment safely",
                f"Translate every line of a real {s['role_name']} job description into a skill",
            ],
            "evidence": "Public README of your home-lab setup + your translated JD as a Gist",
            "rationale": (
                f"Your skill self-rating averages {avg_skill:.1f}/5; we'll close the foundation gap "
                "before going deep so interview vocabulary doesn't trip you up."
            ),
        })
        core_start = p1_end + 1
    else:
        core_start = 1
        # Skipping foundations adds reasonable phase length to phase 2.
        p2_end = max(core_start + 1, weeks // 2)

    # Phase 2: role-specific core skills (always present).
    milestones.append({
        "week_range": f"{core_start}-{p2_end}",
        "title": book["core_title"],
        "objectives": list(book["core_objectives"]),
        "evidence": book["core_evidence"],
        "rationale": book["core_rationale"],
    })

    # Phase 3: certify — gated on budget; if too tight, switch to a free signal.
    # Threshold set at ~$200 because most recruiter-filter certs run $300+.
    if budget >= 200:
        milestones.append({
            "week_range": f"{p2_end+1}-{p3_end}",
            "title": f"Earn {book['cert_name']}",
            "objectives": [
                f"Pass {book['cert_name']} (≈ {book['cert_cost']})",
                "Refactor LinkedIn + résumé to surface the artifacts from phase 2",
                "Set up Google Alerts for the cert + 3 target employer names",
            ],
            "evidence": f"{book['cert_name']} digital badge + updated profile",
            "rationale": (
                "Recruiters use this cert as a filter. Pair it with the artifacts above "
                "or it underperforms."
            ),
        })
    else:
        milestones.append({
            "week_range": f"{p2_end+1}-{p3_end}",
            "title": "Free signal: ISC2 CC + portfolio site",
            "objectives": [
                "Earn ISC2 Certified in Cybersecurity (free)",
                "Build a one-page portfolio site linking to all phase-2 artifacts",
                "Write a 600-word post explaining your transition narrative",
            ],
            "evidence": "ISC2 CC badge + live portfolio URL",
            "rationale": (
                f"Your USD {budget} budget rules out the standard cert filter, so we replace it "
                "with a free credible badge plus a curated portfolio."
            ),
        })

    # Phase 4: apply / interview / iterate (always present).
    milestones.append({
        "week_range": f"{p3_end+1}-{p4_end}",
        "title": "Apply, interview, iterate",
        "objectives": [
            f"5+ targeted applications per week to {book['employer_targets']}",
            "1 mock interview per week using role-specific question banks",
            "2 informational chats per week with people in the role",
        ],
        "evidence": "Application + interview log; first offer is the goal",
        "rationale": "Practice volume beats polish — applied funnel math is on your side here.",
    })

    # Risks: start from role base, layer in profile-aware ones.
    risks = list(book["base_risks"])
    if "weekend" in constraints or "full-time" in constraints or "evenings" in constraints:
        risks.append(
            f"Limited focused time — protect a recurring {hours}-hour block; avoid fragmentation."
        )
    if budget < 200:
        risks.append("Tight budget — lean on free resources (ISC2 CC, BTL1 free, AWS free tier).")
    if avg_skill <= 1.5:
        risks.append("Foundation gap — be honest in interviews, double down on phase-1 evidence.")

    name_clause = f"for {s['name']}" if s["name"] != "you" else "for you"
    summary = (
        f"A {weeks}-week, {hours}h/week roadmap {name_clause} from "
        f"\"{s['background']}\" toward {s['role_name']} in {s['domain_name']}, "
        f"adapted to your skill levels (avg {avg_skill:.1f}/5)"
        + (f" and ${budget} budget" if budget else "")
        + (f"; constraints noted: {s['constraints']}" if s['constraints'] else "")
        + "."
    )

    plan = {
        "summary": summary,
        "milestones": milestones,
        "risks": risks,
        "next_action": book["first_action"],
    }
    return "```json\n" + json.dumps({"plan": plan}, indent=2) + "\n```"


def _retriever(profile: dict, user: str, rng: random.Random) -> str:
    s = _user_summary(profile)
    items = [
        {
            "title": "TryHackMe — SOC Level 1 Path",
            "kind": "lab",
            "url": "https://tryhackme.com/path/outline/soclevel1",
            "why": f"Hands-on triage practice tuned to {s['role_name']} interviews.",
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
        f"Here's a CyberGuide answer tailored to a {s['domain_name']} path toward {s['role_name']}.\n\n"
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
