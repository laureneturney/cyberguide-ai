"""Explore the field — career graph + LLM-augmented domain explanations."""
from __future__ import annotations

import streamlit as st

from ..data import DOMAINS, EVIDENCE_BY_ROLE, list_roles, role_detail
from . import state as S
from .components import card, section_header, pill
from .graph_view import build_graph_figure


def render() -> None:
    section_header("Explore the field", "The cybersecurity career graph at a glance.")

    p = S.profile()
    cols = st.columns([1, 2])

    with cols[0]:
        st.markdown("**Filter the map**")
        domain_id = st.selectbox(
            "Domain",
            options=[""] + [d["id"] for d in DOMAINS],
            format_func=lambda k: "All domains" if not k else next(d["name"] for d in DOMAINS if d["id"] == k),
            index=([""] + [d["id"] for d in DOMAINS]).index(p.preferred_domain or ""),
        )
        roles_pool = list_roles(domain_id or None)
        role_id = st.selectbox(
            "Role to focus",
            options=[""] + [r["id"] for r in roles_pool],
            format_func=lambda k: "Any role" if not k else next(r["name"] for r in roles_pool if r["id"] == k),
            index=0
            if not p.target_role or p.target_role not in [r["id"] for r in roles_pool]
            else 1 + [r["id"] for r in roles_pool].index(p.target_role),
        )

        st.markdown('<div class="cg-divider"></div>', unsafe_allow_html=True)

        explain = st.button("🤖 Explain this corner of the field", use_container_width=True)
        if explain:
            with st.spinner("Asking the Career Graph agent…"):
                # Update profile snapshot used by the agent
                snapshot = p.model_copy(update={"preferred_domain": domain_id or p.preferred_domain,
                                                 "target_role": role_id or p.target_role})
                explanation = S.orch().explain_career_graph(snapshot)
                st.session_state["cg_last_explanation"] = explanation.model_dump()

        last = st.session_state.get("cg_last_explanation")
        if last:
            card(
                "Domain overview",
                f"<span class='cg-muted'>{last['domain_overview']}</span>",
                tags=[("watsonx", "info")],
            )
            card(
                "Key roles",
                "<br>".join(f"• {r}" for r in last["key_roles"]),
            )
            card(
                "Core skills",
                "<br>".join(f"• {s}" for s in last["core_skills"]),
            )
            card(
                "Evidence employers value",
                "<br>".join(f"• {e}" for e in last["evidence_employers_value"]),
                tags=[("Hiring signal", "ok")],
            )

    with cols[1]:
        st.plotly_chart(
            build_graph_figure(highlight_domain=domain_id or None, highlight_role=role_id or None),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        if role_id:
            r = role_detail(role_id)
            if r:
                tags = [
                    (r["seniority"].title(), "ok" if r["seniority"] == "entry" else "info"),
                    (r["salary_band_us"], "info"),
                ]
                evidence = EVIDENCE_BY_ROLE.get(role_id, [])
                card(
                    r["name"],
                    f"<span class='cg-muted'>{r['summary']}</span><br/><br/>"
                    f"<b>Core skills:</b> {', '.join(r['core_skills'])}<br/>"
                    f"<b>Typical employers:</b> {', '.join(r['typical_employers'])}<br/><br/>"
                    f"<b>Evidence employers want:</b><br>"
                    + "".join(f"&nbsp;• {e}<br>" for e in evidence),
                    tags=tags,
                )
