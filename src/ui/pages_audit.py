"""Audit & Trust page — surfaces every agent action for transparency."""
from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from . import state as S
from .components import card, section_header


def render() -> None:
    section_header(
        "Audit & trust",
        "Every recommendation in this session, with rationale and provenance.",
    )

    audit = S.orch().audit
    if not audit:
        st.markdown(
            '<div class="cg-card"><span class="cg-muted">No agent activity yet — interact with the app to populate the trail.</span></div>',
            unsafe_allow_html=True,
        )
        return

    df = pd.DataFrame(
        [
            {
                "When (UTC)": a.when,
                "Agent": a.agent,
                "Action": a.action,
                "Summary": a.summary,
            }
            for a in audit
        ]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander("View raw audit payloads (JSON)"):
        st.code(
            json.dumps(
                [
                    {
                        "when": a.when,
                        "agent": a.agent,
                        "action": a.action,
                        "summary": a.summary,
                        "payload": a.payload,
                    }
                    for a in audit
                ],
                indent=2,
            ),
            language="json",
        )

    section_header("Responsible-AI principles in this build", "")
    cols = st.columns(2)
    with cols[0]:
        card("Fairness", "Every output is tied to the user's specific profile and constraints — no one-size advice.")
        card("Transparency", "Each plan/decision includes a rationale; this page shows the audit trail.")
        card("No fabrication", "URLs and roles come from the curated graph; the retriever drops links the model invents.")
    with cols[1]:
        card("Human-in-the-loop", "Decisions are surfaced as trade-offs requiring user confirmation.")
        card("Privacy", "Profile and chat live only in this Streamlit session — no persistence across reloads.")
        card("Accountability", "Every action is timestamped and attributed to a named agent.")
