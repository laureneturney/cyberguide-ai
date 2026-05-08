"""Home / dashboard page."""
from __future__ import annotations

import streamlit as st

from . import state as S
from .components import card, section_header, pill, _render_html


def render() -> None:
    section_header(
        "Welcome to CyberGuide.AI",
        "An agentic, transparent navigator for your path into cybersecurity.",
    )

    has_plan = S.st.session_state[S.K_PLAN] is not None
    n_decisions = len(S.st.session_state[S.K_DECISIONS])
    n_chat = len(S.st.session_state[S.K_CHAT])

    cols = st.columns(3)
    with cols[0]:
        card(
            "Roadmap",
            "<span class='cg-muted'>No plan generated yet — head to Roadmap to start.</span>"
            if not has_plan
            else f"<b>{S.st.session_state[S.K_PLAN].milestones[0].title if S.st.session_state[S.K_PLAN].milestones else 'Generated'}</b>"
            f"<br><span class='cg-muted'>{len(S.st.session_state[S.K_PLAN].milestones)} milestones</span>",
            tags=[("Ready", "ok") if has_plan else ("Pending", "warn")],
        )
    with cols[1]:
        card(
            "Decisions",
            f"<b>{n_decisions}</b> recorded",
            meta="Forks reviewed with rationale",
            tags=[("Auditable", "info")],
        )
    with cols[2]:
        card(
            "Chat",
            f"<b>{n_chat // 2}</b> question{'s' if n_chat // 2 != 1 else ''} this session",
            meta="Free-form questions, profile-aware",
            tags=[("Active", "ok") if n_chat else ("Idle", "warn")],
        )

    _render_html('<div class="cg-divider"></div>')

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

    _render_html('<div class="cg-divider"></div>')

    section_header("Get started", "")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Build your roadmap", use_container_width=True, key="home_btn_plan"):
            S.st.session_state[S.K_PAGE] = "Roadmap"
            st.rerun()
    with c2:
        if st.button("🗺️ Explore the field", use_container_width=True, key="home_btn_explore"):
            S.st.session_state[S.K_PAGE] = "Explore"
            st.rerun()

    _render_html(
        '<div class="cg-card" style="margin-top:18px;">'
        '<h4>Why this is built differently</h4>'
        '<ul style="margin: 6px 0 0 18px; color: var(--cg-text); font-size:13px;">'
        '<li><b>Personalized</b> to your background, hours, and timeline — not one-size-fits-all.</li>'
        '<li><b>Transparent</b>: every recommendation comes with a rationale you can challenge.</li>'
        '<li><b>Human-in-the-loop</b> on key forks: the agent advises; you decide.</li>'
        '<li><b>No fabrication</b>: when knowledge is thin, CyberGuide says so and uses fallback templates.</li>'
        '</ul>'
        '</div>'
    )
