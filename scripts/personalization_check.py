"""Verify the mock pathfinder actually produces visibly different plans
for visibly different profiles.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents import Orchestrator, UserProfile

o = Orchestrator()


def show(label: str, plan):
    print(f"\n=== {label} ===")
    print("summary:", plan.summary)
    print(f"milestones ({len(plan.milestones)}):")
    for m in plan.milestones:
        print(f"  - [{m.week_range}] {m.title}")
    print("risks:")
    for r in plan.risks:
        print(f"  - {r}")
    print("next_action:", plan.next_action)


# Profile A: SOC, low skills, tight budget, weekend-only
a = UserProfile(
    name="Sara",
    background="2 years restaurant management",
    weekly_hours=6,
    timeline_weeks=20,
    budget_usd=120,
    constraints="Working full-time; weekends only.",
    preferred_domain="soc",
    target_role="soc_t1",
    skills_self_rated={"Networking": 1, "Linux": 1, "Windows": 1},
)

# Profile B: AppSec, high skills, healthy budget, no constraints
b = UserProfile(
    name="Devon",
    background="6 years backend engineer at fintech",
    weekly_hours=15,
    timeline_weeks=12,
    budget_usd=2000,
    constraints="",
    preferred_domain="appsec",
    target_role="appsec_eng",
    skills_self_rated={
        "Networking": 4, "Linux": 5, "Windows": 4,
        "Scripting (Python or PowerShell)": 5, "Cloud (AWS/Azure/GCP)": 4,
    },
)

# Profile C: GRC, mid skills, paid bootcamp budget, family constraints
c = UserProfile(
    name="Maya",
    background="Auditor at Big 4, 4 years",
    weekly_hours=10,
    timeline_weeks=24,
    budget_usd=800,
    constraints="Two kids; evenings only after 9pm.",
    preferred_domain="grc",
    target_role="grc_analyst",
    skills_self_rated={"Networking": 2, "Windows": 3},
)

plan_a = o.make_plan(a)
plan_b = o.make_plan(b)
plan_c = o.make_plan(c)

show("Sara — SOC T1, beginner, $120, weekends", plan_a)
show("Devon — AppSec engineer, advanced, $2000, free schedule", plan_b)
show("Maya — GRC analyst, mid, $800, evenings only", plan_c)

# Hard assertions: plans must NOT be identical.
sigs = {
    "a": (plan_a.summary, tuple(m.title for m in plan_a.milestones)),
    "b": (plan_b.summary, tuple(m.title for m in plan_b.milestones)),
    "c": (plan_c.summary, tuple(m.title for m in plan_c.milestones)),
}
assert sigs["a"] != sigs["b"], "SOC and AppSec plans should differ"
assert sigs["b"] != sigs["c"], "AppSec and GRC plans should differ"
assert sigs["a"] != sigs["c"], "SOC and GRC plans should differ"

# Foundation gating: high-skill profile B should skip foundations.
assert "foundation" not in plan_b.milestones[0].title.lower(), \
    "Devon (avg skill 4.4) should NOT get a foundations milestone"
assert "foundation" in plan_a.milestones[0].title.lower() or \
       "foundations" in plan_a.milestones[0].title.lower(), \
    "Sara (avg skill 1.0) SHOULD get a foundations milestone"

# Budget gating: tight-budget Sara should see ISC2 CC, not Sec+ in cert phase.
assert any("ISC2" in m.title or "free" in m.title.lower() for m in plan_a.milestones), \
    "Sara's $120 budget should trigger free-signal cert path"
assert any("OSWE" in m.title or "OWASP" in m.title for m in plan_b.milestones) or \
       any("appsec" in m.title.lower() or "threat" in m.title.lower() for m in plan_b.milestones), \
    "Devon's plan should be appsec-flavored"

# Constraints reflected in risks.
assert any("weekend" in r.lower() or "fragment" in r.lower() for r in plan_a.risks), \
    "Sara's weekend-only constraint should appear in risks"
assert any("evening" in r.lower() or "fragment" in r.lower() for r in plan_c.risks), \
    "Maya's evening-only constraint should appear in risks"

print("\n✅ Personalization assertions all passed")
