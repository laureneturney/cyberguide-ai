"""Home / dashboard page."""
from __future__ import annotations

import streamlit as st

from . import state as S
from .components import card, section_header, pill


def render() -> None:
    section_header(
        "Welcome to CyberGuide.AI",
        "An agentic, transparent navigator for your path into cybersecurity.",
    )

    p = S.profile()
    has_profile = bool(p.preferred_domain or p.target_role)
    has_plan = S.st.session_state[S.K_PLAN] is not None
    n_decisions = len(S.st.session_state[S.K_DECISIONS])

    cols = st.columns(3)
    with cols[0]:
        card(
            "Profile",
            f"<b>{p.name or '—'}</b><br><span class='cg-muted'>"
            f"{p.background or 'No background captured'}</span>",
            meta=f"{p.weekly_hours or 0} hrs/wk · {p.timeline_weeks or 0} wks",
            tags=[("Captured", "ok") if has_profile else ("Empty", "warn")],
        )
    with cols[1]:
        card(
            "Roadmap",
            "<span class='cg-muted'>No plan generated yet.</span>"
            if not has_plan
            else f"<b>{S.st.session_state[S.K_PLAN].milestones[0].title if S.st.session_state[S.K_PLAN].milestones else 'Generated'}</b>"
            f"<br><span class='cg-muted'>{len(S.st.session_state[S.K_PLAN].milestones)} milestones</span>",
            tags=[("Ready", "ok") if has_plan else ("Pending", "warn")],
        )
    with cols[2]:
        card(
            "Decisions",
            f"<b>{n_decisions}</b> recorded",
            meta="Forks reviewed with rationale",
            tags=[("Auditable", "info")],
        )

    st.markdown('<div class="cg-divider"></div>', unsafe_allow_html=True)

    section_header("How CyberGuide works", "Four coordinated agents — one career navigation system.")
    g = st.columns(4)
    agents = [
        ("Career Graph", "Maps domains, roles, and the evidence employers value."),
        ("Pathfinder", "Builds and re-plans a personalized week-by-week roadmap."),
        ("Resource Retriever", "Pulls the right resources at the right moment."),
        ("Decision Support", "Walks you through forks with trade-offs and rationale."),
    ]
    for col, (title, body) in zip(g, agents):
        with col:
            card(title, f"<span class='cg-muted'>{body}</span>")

    st.markdown('<div class="cg-divider"></div>', unsafe_allow_html=True)

    section_header("Get started", "")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("👤 Build your profile", use_container_width=True, key="home_btn_profile"):
            S.st.session_state[S.K_PAGE] = "Profile"
            st.rerun()
    with c2:
        if st.button("🗺️ Explore the field", use_container_width=True, key="home_btn_explore"):
            S.st.session_state[S.K_PAGE] = "Explore"
            st.rerun()
    with c3:
        if st.button("🚀 Generate a roadmap", use_container_width=True, key="home_btn_plan"):
            S.st.session_state[S.K_PAGE] = "Roadmap"
            st.rerun()

    st.markdown(
        f"""
<div class="cg-card" style="margin-top:18px;">
    <h4>Why this is built differently</h4>
    <ul style="margin: 6px 0 0 18px; color: var(--cg-text); font-size:13px;">
      <li><b>Personalized</b> to your background, hours, and timeline — not one-size-fits-all.</li>
      <li><b>Transparent</b>: every recommendation comes with a rationale you can challenge.</li>
      <li><b>Human-in-the-loop</b> on key forks: the agent advises; you decide.</li>
      <li><b>No fabrication</b>: when knowledge is thin, CyberGuide says so and uses fallback templates.</li>
    </ul>
</div>
""",
        unsafe_allow_html=True,
    )
