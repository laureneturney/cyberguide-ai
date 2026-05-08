"""Conversational chat with CyberGuide."""
from __future__ import annotations

import streamlit as st

from . import state as S
from .components import _render_html, chat_bubble, section_header


_SUGGESTIONS = [
    "What should I build first to land a SOC role in 4 months?",
    "Is Security+ or ISC2 CC the better first cert for my profile?",
    "How do I turn 3 years of helpdesk into convincing cyber experience?",
    "What's a realistic 8-hour-a-week study plan for me?",
]


def render() -> None:
    section_header(
        "Chat with CyberGuide",
        "Ask anything — the agent uses your saved profile for context.",
    )

    p = S.profile()
    history: list[tuple[str, str]] = S.st.session_state[S.K_CHAT]

    # Welcome card + click-to-ask suggestions when the conversation is empty.
    if not history:
        _render_html(
            '<div class="cg-card">'
            "<b>Welcome.</b> "
            "<span class='cg-muted'>Ask CyberGuide about domains, roles, certs, "
            "or the next step on your roadmap. Suggestions below — click any to send.</span>"
            "</div>"
        )
        cols = st.columns(2)
        for i, suggestion in enumerate(_SUGGESTIONS):
            with cols[i % 2]:
                if st.button(f"💡 {suggestion}", key=f"cg_chat_suggest_{i}", use_container_width=True):
                    _ask(p, history, suggestion)

    # Render existing history.
    for role, content in history:
        chat_bubble(role, content)

    # Bottom-anchored chat input. Streamlit positions this at the page bottom.
    user_msg = st.chat_input("Ask CyberGuide…")
    if user_msg:
        _ask(p, history, user_msg)


def _ask(profile, history: list[tuple[str, str]], user_msg: str) -> None:
    """Run a single chat turn and force a clean rerender."""
    try:
        with st.spinner("CyberGuide is thinking…"):
            # Pass history WITHOUT the new user message; the orchestrator appends it.
            reply = S.orch().chat(profile, history, user_msg)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Chat error: {exc}")
        return
    history.append(("user", user_msg))
    history.append(("assistant", reply))
    st.rerun()
