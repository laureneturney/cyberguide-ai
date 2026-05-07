"""Conversational chat with CyberGuide."""
from __future__ import annotations

import streamlit as st

from . import state as S
from .components import section_header, chat_bubble, _render_html


def render() -> None:
    section_header("Chat with CyberGuide", "Ask anything — the agent uses your saved profile for context.")

    p = S.profile()
    history = S.st.session_state[S.K_CHAT]

    chat_box = st.container()
    with chat_box:
        if not history:
            _render_html(
                '<div class="cg-card"><span class="cg-muted">'
                'Start the conversation — try: <i>“What should I build first to land a SOC role in 4 months?”</i>'
                '</span></div>'
            )
        for role, content in history:
            chat_bubble(role, content)

    user_msg = st.chat_input("Ask CyberGuide…")
    if user_msg:
        history.append(("user", user_msg))
        with st.spinner("CyberGuide is thinking…"):
            reply = S.orch().chat(p, history, user_msg)
        history.append(("assistant", reply))
        st.rerun()
