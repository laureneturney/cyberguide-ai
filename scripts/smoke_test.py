"""Headless smoke test — exercises each agent end-to-end with the mock provider.

Run from the project root:
    python scripts/smoke_test.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents import DecisionRequest, Orchestrator, UserProfile
from src.config import settings
from src.data import DOMAINS, ROLES
from src.tools import web_search


def main() -> int:
    print(f"settings.provider={settings.provider!r}  display={settings.display_provider_name!r}")
    print(f"loaded {len(DOMAINS)} domains, {len(ROLES)} roles")

    o = Orchestrator()
    print(f"orchestrator.actual_provider={o.actual_provider}  display={o.display_provider}  model={o.display_model}")

    profile = UserProfile(
        name="Jordan",
        background="3 years IT helpdesk",
        education="BA, History",
        weekly_hours=8,
        timeline_weeks=16,
        budget_usd=400,
        constraints="full-time job, weekends only",
        preferred_domain="soc",
        target_role="soc_t1",
        skills_self_rated={"Networking": 2, "Linux": 2},
        interests=["Security Operations (SOC)", "DFIR"],
    )

    g = o.explain_career_graph(profile)
    assert g.domain_overview, "graph explanation must have a domain overview"
    print("✓ career graph:", g.common_first_role)

    plan = o.make_plan(profile)
    assert plan.summary and plan.milestones, "plan must have summary + milestones"
    print(f"✓ plan: {len(plan.milestones)} milestones, next='{plan.next_action[:60]}'")

    resources = o.retrieve_resources(profile, focus="home lab on a budget")
    assert resources, "retriever must return at least one resource"
    print(f"✓ retriever: {len(resources)} items, first='{resources[0].title}'")

    decision = o.decide(
        profile,
        DecisionRequest(
            question="Security+ or ISC2 CC first?",
            options=["CompTIA Security+", "ISC2 CC"],
        ),
    )
    assert decision.recommendation in {o.label for o in decision.options}, "recommendation must match an option"
    print(f"✓ decision: '{decision.recommendation}' (confidence={decision.confidence:.2f})")

    chat_reply = o.chat(profile, [], "What's the smallest first step I can take this weekend?")
    assert chat_reply, "chat must return text"
    print(f"✓ chat reply ({len(chat_reply)} chars)")

    print("\n--- audit trail ---")
    for entry in o.audit:
        print(f"  [{entry.when}] {entry.agent}.{entry.action} — {entry.summary}")

    # web search smoke (degrades gracefully)
    hits = web_search("CompTIA Security+ syllabus 2026", max_results=2)
    print(f"\nweb_search returned {len(hits)} hits (source: {hits[0].source if hits else 'none'})")

    # Resume profiler end-to-end
    sample_resume = """
    Jordan Smith — Career Changer
    Education: B.A. in History, 2020.
    Experience: 3 years IT helpdesk at a regional bank — ticket triage, AD password resets, basic networking.
    Built a home Splunk lab on Sysmon-instrumented Windows VMs.
    Published 4 TryHackMe SOC L1 walkthroughs on a personal blog.
    Studying for CompTIA Security+ (SY0-701).
    """
    analysis = o.analyze_resume(sample_resume)
    assert analysis.suggested_role_id, "profiler should suggest a role"
    print(f"✓ resume profiler: suggested {analysis.suggested_role_id} "
          f"in {analysis.suggested_domain_id} (confidence={analysis.confidence:.2f})")
    print(f"  skills detected: {list(analysis.skills_detected.items())[:3]}")
    merged = o.apply_resume_to_profile(UserProfile(), analysis)
    assert merged.preferred_domain == analysis.suggested_domain_id
    print(f"✓ profile merge produced domain={merged.preferred_domain} role={merged.target_role}")

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
