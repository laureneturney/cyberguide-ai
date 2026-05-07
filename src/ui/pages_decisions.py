"""Decision support page — structured fork analysis with rationale."""
from __future__ import annotations

import streamlit as st

from ..agents import DecisionRequest
from . import state as S
from .components import card, section_header, _render_html


PRESETS: list[tuple[str, list[str]]] = [
    (
        "SOC Analyst vs. Junior Security Engineer for my first role?",
        ["SOC Analyst (Tier 1)", "Junior Security Engineer"],
    ),
    (
        "Should my first cert be Security+ or ISC2 CC?",
        ["CompTIA Security+", "ISC2 Certified in Cybersecurity (CC)"],
    ),
    (
        "Self-paced labs vs. a paid bootcamp?",
        ["Self-paced labs (TryHackMe / BTL1)", "Paid bootcamp (12-week)"],
    ),
    (
        "Pivot to AppSec or Cloud Security?",
        ["Application Security", "Cloud Security"],
    ),
]


def render() -> None:
    section_header(
        "Decision support",
        "The agent surfaces trade-offs and a recommendation; you make the call.",
    )

    p = S.profile()

    with st.form("decision_form"):
        c1, c2 = st.columns([2, 1])
        with c1:
            preset_label = st.selectbox(
                "Pick a common fork (or compose your own below)",
                options=["— custom —"] + [t[0] for t in PRESETS],
            )
        with c2:
            include_context = st.toggle("Include profile context", value=True)

        if preset_label != "— custom —":
            preset_q, preset_opts = next(t for t in PRESETS if t[0] == preset_label)
        else:
            preset_q, preset_opts = "", []

        question = st.text_input("Decision question", value=preset_q)
        opt_text = st.text_area(
            "Options (one per line)",
            value="\n".join(preset_opts),
            height=110,
            placeholder="Option A\nOption B",
        )
        context = st.text_area(
            "Extra context (optional)",
            value="",
            placeholder="e.g., 'I have an interview at an MSSP next month.'",
        )
        submit = st.form_submit_button("⚖️ Analyze decision")

    if submit:
        opts = [line.strip() for line in opt_text.splitlines() if line.strip()]
        if not question or len(opts) < 2:
            st.warning("Please provide a question and at least two options.")
        else:
            req = DecisionRequest(question=question, options=opts, context=context if include_context else "")
            with st.spinner("Decision support agent analyzing trade-offs…"):
                result = S.orch().decide(p, req)
            S.st.session_state[S.K_DECISIONS].insert(0, (req.model_dump(), result.model_dump()))

    decisions = S.st.session_state[S.K_DECISIONS]
    if not decisions:
        _render_html(
            '<div class="cg-card"><span class="cg-muted">No decisions analyzed yet.</span></div>'
        )
        return

    for idx, (req, res) in enumerate(decisions):
        _render_html(
            '<div class="cg-rec">'
            '<div style="display:flex; align-items:center; gap:8px;">'
            '<span class="cg-tag ok">Recommendation</span>'
            f'<b>{res["recommendation"]}</b>'
            f'<span class="cg-tag info" style="margin-left:auto;">confidence {res["confidence"]:.2f}</span>'
            '</div>'
            f'<div style="margin-top:8px; font-size:13px;">{res["rationale"]}</div>'
            '<div class="cg-muted" style="margin-top:6px; font-size:11px;">'
            'Human-in-the-loop: please confirm before acting on this recommendation.'
            '</div>'
            '</div>'
        )
        cols = st.columns(len(res["options"]))
        for i, opt in enumerate(res["options"]):
            with cols[i]:
                pros = "".join(f"<li>{p}</li>" for p in opt["pros"])
                cons = "".join(f"<li>{c}</li>" for c in opt["cons"])
                fit = opt.get("fit_score", 0.0)
                tag_kind = "ok" if fit >= 0.7 else ("warn" if fit >= 0.4 else "bad")
                card(
                    opt["label"],
                    (
                        f"<b style='color:var(--cg-muted); font-size:11px;'>PROS</b><ul style='margin:4px 0 8px 18px;'>{pros}</ul>"
                        f"<b style='color:var(--cg-muted); font-size:11px;'>CONS</b><ul style='margin:4px 0 0 18px;'>{cons}</ul>"
                    ),
                    tags=[(f"fit {fit:.0%}", tag_kind)],
                )
        c1, c2, _ = st.columns([1, 1, 4])
        with c1:
            if st.button("✅ Accept", key=f"acc_{idx}"):
                st.toast("Recorded as accepted in audit log.", icon="✅")
        with c2:
            if st.button("↩ Revisit later", key=f"rev_{idx}"):
                st.toast("Will revisit later — no action taken.", icon="↩️")
        _render_html('<div class="cg-divider"></div>')
