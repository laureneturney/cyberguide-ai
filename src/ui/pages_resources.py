"""Just-in-time resources page — retriever agent + live web search."""
from __future__ import annotations

import streamlit as st

from . import state as S
from .components import card, section_header


def render() -> None:
    section_header(
        "Just-in-time resources",
        "The Retriever agent surfaces only what's useful for your current step.",
    )
    p = S.profile()

    c1, c2 = st.columns([3, 1])
    with c1:
        focus = st.text_input(
            "Focus (optional)",
            value="",
            placeholder="e.g., 'how to build a Splunk lab on a 16GB laptop'",
        )
    with c2:
        n = st.slider("Max results", 3, 8, 5)

    if st.button("🔎 Retrieve resources", use_container_width=True):
        with st.spinner("Retriever agent pulling curated + live results…"):
            results = S.orch().retrieve_resources(p, focus=focus, max_results=n)
            S.st.session_state[S.K_RESOURCES] = [r.model_dump() for r in results]

    results = S.st.session_state[S.K_RESOURCES]
    if not results:
        st.markdown(
            '<div class="cg-card"><span class="cg-muted">'
            "No resources retrieved yet. Click <b>Retrieve resources</b> above."
            "</span></div>",
            unsafe_allow_html=True,
        )
        return

    grid = st.columns(2)
    for i, r in enumerate(results):
        with grid[i % 2]:
            tags = [(r["kind"], "info")]
            if r.get("source") == "web":
                tags.append(("Live web", "warn"))
            elif r.get("source") == "curated":
                tags.append(("Curated", "ok"))
            url = r.get("url") or "#"
            card(
                r.get("title", "Untitled"),
                (
                    f"<a href='{url}' target='_blank'>{url}</a><br><br>"
                    f"<span class='cg-muted'>{r.get('why', '')}</span>"
                ),
                meta=f"{r.get('cost', '—')}  ·  {r.get('time_estimate', '—')}",
                tags=tags,
            )
