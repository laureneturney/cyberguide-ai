"""Profile builder page."""
from __future__ import annotations

import streamlit as st

from ..agents import UserProfile
from ..data import DOMAINS, ROLES
from . import state as S
from .components import section_header


def render() -> None:
    section_header("Your profile", "Personalization starts here. Everything stays in this session only.")

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
