"""Profile page — resume upload + structured profile builder.

Top section: drag-and-drop a resume (PDF / DOCX / TXT) or paste a list of
courses + experiences. The Resume Profiler agent extracts a structured
analysis, prefills the form below, and offers one-click roadmap generation.

Bottom section: a fully-editable form for everything the agent inferred (or
for users who want to skip the upload entirely).
"""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

from ..agents import UserProfile
from ..data import DOMAINS, ROLES, domain_detail, role_detail
from ..tools import parse_paste, parse_upload
from . import state as S
from .components import card, section_header, _render_html


# -----------------------------------------------------------------------------
# Resume upload section
# -----------------------------------------------------------------------------


def _render_resume_section() -> None:
    section_header(
        "Build your profile from a resume",
        "Upload a PDF/DOCX or paste your courses + experiences. CyberGuide infers your starting point.",
    )

    tab_upload, tab_paste = st.tabs(["📄 Upload file", "✍️ Paste text"])

    resume_text = ""
    resume_source_label = ""
    with tab_upload:
        uploaded = st.file_uploader(
            "Drop a PDF, DOCX, or TXT (we don't store anything — session only).",
            type=["pdf", "docx", "txt", "md"],
            accept_multiple_files=False,
            key="resume_upload",
        )
        if uploaded is not None:
            data = uploaded.getvalue()
            parsed = parse_upload(uploaded.name, data)
            if parsed.text:
                resume_text = parsed.text
                resume_source_label = f"file: {uploaded.name} ({parsed.char_count:,} chars)"
                st.success(
                    f"Parsed {parsed.source.upper()}: {parsed.char_count:,} characters extracted.",
                    icon="✅",
                )
            else:
                st.error(
                    f"Could not extract text from this file. {parsed.notes or 'Try pasting the content instead.'}"
                )

    with tab_paste:
        pasted = st.text_area(
            "Paste resume text, course list, or a free-form summary",
            value=S.st.session_state.get(S.K_RESUME_TEXT, ""),
            height=200,
            key="resume_paste",
            placeholder=(
                "e.g.\n"
                "Courses: Networking Fundamentals (Cisco), Linux Essentials, Intro to Cloud (AWS).\n"
                "Experience: 2 yrs IT helpdesk; built a home Splunk lab; published 3 TryHackMe write-ups.\n"
                "Certifications: Security+ in progress."
            ),
        )
        if pasted and pasted.strip():
            parsed = parse_paste(pasted)
            resume_text = parsed.text
            resume_source_label = f"pasted ({parsed.char_count:,} chars)"

    cols = st.columns([1, 1, 2])
    with cols[0]:
        analyze_clicked = st.button(
            "🤖 Analyze & build profile",
            use_container_width=True,
            disabled=not resume_text,
        )
    with cols[1]:
        autoplan_after = st.toggle("Auto-generate roadmap", value=True)

    if analyze_clicked and resume_text:
        S.st.session_state[S.K_RESUME_TEXT] = resume_text
        with st.spinner("Resume Profiler agent reading your background…"):
            analysis = S.orch().analyze_resume(resume_text)
            S.st.session_state[S.K_RESUME_ANALYSIS] = analysis.model_dump()
            merged = S.orch().apply_resume_to_profile(S.profile(), analysis)
            S.set_profile(merged)
            if autoplan_after and (merged.preferred_domain or merged.target_role):
                plan = S.orch().make_plan(merged)
                S.st.session_state[S.K_PLAN] = plan
                S.st.session_state[S.K_MILESTONE_PROGRESS] = {
                    i: False for i in range(len(plan.milestones))
                }
        st.toast(f"Profile updated from {resume_source_label}.", icon="✅")
        st.rerun()

    last = S.st.session_state.get(S.K_RESUME_ANALYSIS)
    if last:
        _render_analysis_card(last)


def _render_analysis_card(analysis: dict[str, Any]) -> None:
    domain_id = analysis.get("suggested_domain_id") or ""
    role_id = analysis.get("suggested_role_id") or ""
    domain_name = (domain_detail(domain_id) or {}).get("name", "—")
    role_name = (role_detail(role_id) or {}).get("name", "—")
    confidence = float(analysis.get("confidence") or 0.0)
    conf_kind = "ok" if confidence >= 0.7 else ("warn" if confidence >= 0.4 else "bad")

    skills = analysis.get("skills_detected") or {}
    skill_html = "".join(
        f'<span class="cg-tag info">{html.escape(k)}<span style="opacity:.7;"> · {int(v)}/5</span></span>'
        for k, v in skills.items()
    ) or '<span class="cg-muted">No skills detected.</span>'
    certs = analysis.get("certifications") or []
    cert_html = "".join(f'<span class="cg-tag ok">{html.escape(c)}</span>' for c in certs) or '<span class="cg-muted">None detected.</span>'
    gaps = analysis.get("gaps_for_target") or []
    gap_html = "".join(f"<li>{html.escape(g)}</li>" for g in gaps) or "<li>No major gaps flagged.</li>"

    body = (
        f"<div class='cg-muted' style='margin-bottom:8px;'>{html.escape(analysis.get('summary',''))}</div>"
        f"<div style='display:flex; flex-wrap:wrap; gap:14px; margin-top:6px;'>"
        f"<div><b>Suggested domain:</b> {html.escape(domain_name)}</div>"
        f"<div><b>Suggested role:</b> {html.escape(role_name)}</div>"
        f"<div><b>Years:</b> {float(analysis.get('estimated_years_experience', 0)):.1f}</div>"
        f"</div>"
        f"<div style='margin-top:12px;'><b style='font-size:12px; color:var(--cg-muted);'>SKILLS</b><br>{skill_html}</div>"
        f"<div style='margin-top:10px;'><b style='font-size:12px; color:var(--cg-muted);'>CERTIFICATIONS</b><br>{cert_html}</div>"
        f"<div style='margin-top:10px;'><b style='font-size:12px; color:var(--cg-muted);'>GAPS FOR THE SUGGESTED ROLE</b><ul style='margin:4px 0 0 18px;'>{gap_html}</ul></div>"
        f"<div style='margin-top:10px; font-style:italic; color:var(--cg-muted);'>"
        f"Why: {html.escape(analysis.get('rationale',''))}</div>"
    )
    card(
        "Resume analysis",
        body,
        meta="Generated by the Resume Profiler agent",
        tags=[(f"confidence {confidence:.0%}", conf_kind), ("watsonx", "info")],
    )


# -----------------------------------------------------------------------------
# Manual profile form (existing flow)
# -----------------------------------------------------------------------------


def _render_form() -> None:
    section_header("Or edit your profile manually", "Everything below is editable — the agent's suggestions are just a starting point.")
    p = S.profile()

    with st.form("profile_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Preferred name", value=p.name, placeholder="Jordan")
            background = st.text_input(
                "Where you're coming from",
                value=p.background,
                placeholder="e.g., 'IT helpdesk for 3 years' or 'recent CS grad'",
            )
            education = st.text_input("Highest education or relevant credential", value=p.education)
            location = st.text_input("Location (optional)", value=p.location, placeholder="Atlanta, GA")
        with c2:
            weekly_hours = st.slider("Weekly study hours", 2, 30, p.weekly_hours or 8)
            timeline_weeks = st.slider("Target timeline (weeks)", 4, 52, p.timeline_weeks or 16)
            budget_usd = st.number_input(
                "Budget for certs/labs (USD, total)",
                min_value=0,
                max_value=10000,
                value=p.budget_usd or 500,
                step=50,
            )
            constraints = st.text_area(
                "Constraints, in your own words",
                value=p.constraints,
                placeholder="Working full-time, only weekends; no work auth for federal roles; etc.",
            )

        st.markdown("**Where do you want to focus?**")
        d_options = {"": "— pick a domain —"} | {d["id"]: d["name"] for d in DOMAINS}
        preferred_domain = st.selectbox(
            "Preferred domain",
            options=list(d_options.keys()),
            format_func=lambda k: d_options[k],
            index=list(d_options.keys()).index(p.preferred_domain) if p.preferred_domain in d_options else 0,
        )

        roles_in_scope = [r for r in ROLES if not preferred_domain or r["domain_id"] == preferred_domain]
        r_options = {"": "— pick a target role —"} | {r["id"]: r["name"] for r in roles_in_scope}
        target_role = st.selectbox(
            "Target role",
            options=list(r_options.keys()),
            format_func=lambda k: r_options[k],
            index=list(r_options.keys()).index(p.target_role) if p.target_role in r_options else 0,
        )

        st.markdown("**Skills self-assessment (1 = none, 5 = strong)**")
        skill_cols = st.columns(2)
        skills_input = {}
        skill_keys = [
            "Networking",
            "Linux",
            "Windows",
            "Scripting (Python or PowerShell)",
            "Cloud (AWS/Azure/GCP)",
            "Security tooling (SIEM/EDR)",
        ]
        for i, key in enumerate(skill_keys):
            with skill_cols[i % 2]:
                skills_input[key] = st.slider(key, 1, 5, p.skills_self_rated.get(key, 1), key=f"skill_{key}")

        interests = st.multiselect(
            "Interests (pick any)",
            options=[d["name"] for d in DOMAINS],
            default=p.interests,
        )

        save = st.form_submit_button("💾 Save profile")

    if save:
        new_p = UserProfile(
            name=name.strip(),
            background=background.strip(),
            education=education.strip(),
            location=location.strip(),
            weekly_hours=int(weekly_hours),
            timeline_weeks=int(timeline_weeks),
            budget_usd=int(budget_usd),
            constraints=constraints.strip(),
            preferred_domain=preferred_domain,
            target_role=target_role,
            skills_self_rated=skills_input,
            interests=interests,
        )
        S.set_profile(new_p)
        st.success("Profile saved for this session.")
        st.toast("Profile saved", icon="✅")


def render() -> None:
    _render_resume_section()
    _render_html('<div class="cg-divider"></div>')
    _render_form()
