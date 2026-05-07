"""CyberGuide.AI — Streamlit entry point.

Run locally:    streamlit run streamlit_app.py
Deploy on Streamlit Cloud: just point it at this file in the repo root.
"""
from __future__ import annotations

import os

import streamlit as st


# Bridge Streamlit Cloud secrets into os.environ BEFORE the rest of the app
# imports `src.config` (which reads via os.getenv). On Streamlit Cloud,
# secrets entered as TOML are exposed only via st.secrets, not as env vars,
# so without this hop our config layer would never see them.
def _bridge_secrets_to_env() -> None:
    try:
        # st.secrets raises lazily when no secrets file is present, so the
        # whole iteration has to be inside the try block — not just the access.
        for key in st.secrets:
            value = st.secrets.get(key)
            if isinstance(value, (str, int, float, bool)) and key not in os.environ:
                os.environ[key] = str(value)
    except Exception:
        return


_bridge_secrets_to_env()

from src.config import settings  # noqa: E402  (import after bridge by design)
from src.ui import state as S
from src.ui.theme import inject_css, brand_bar
from src.ui.components import _render_html
from src.ui import (
    pages_home,
    pages_profile,
    pages_explore,
    pages_roadmap,
    pages_resources,
    pages_decisions,
    pages_chat,
    pages_audit,
)


PAGES: dict[str, callable] = {
    "Home": pages_home.render,
    "Profile": pages_profile.render,
    "Explore": pages_explore.render,
    "Roadmap": pages_roadmap.render,
    "Resources": pages_resources.render,
    "Decisions": pages_decisions.render,
    "Chat": pages_chat.render,
    "Audit & Trust": pages_audit.render,
}


def main() -> None:
    st.set_page_config(
        page_title="CyberGuide.AI",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    S.ensure_state()

    with st.sidebar:
        # IBM watsonx is always shown to the user, regardless of LLM_PROVIDER.
        _render_html(
            "<div style='padding:14px 8px 6px 8px;'>"
            "<div style='font-weight:700; font-size:18px;'>CyberGuide.AI</div>"
            f"<div style='color:#8b97ad; font-size:11px; margin-top:2px;'>"
            f"Powered by <b>IBM watsonx</b> · {S.orch().display_model}"
            "</div>"
            "</div>"
        )

        _render_html('<div style="height:6px;"></div>')
        for label in PAGES.keys():
            is_active = S.st.session_state[S.K_PAGE] == label
            btn_label = f"{'●  ' if is_active else '○  '}{label}"
            if st.button(btn_label, key=f"nav_{label}", use_container_width=True):
                S.st.session_state[S.K_PAGE] = label
                st.rerun()

        _render_html('<div class="cg-divider"></div>')
        with st.expander("Session controls"):
            if st.button("🧹 Reset session", use_container_width=True):
                S.reset_session()
                st.rerun()
            st.caption("Session-only persistence — reloading the page clears the demo state.")

        _render_html('<div class="cg-divider"></div>')
        st.caption(
            "Service provider: **IBM watsonx**\n\n"
            "Switch backends via `.env` — the UI stays branded watsonx by design."
        )

    brand_bar(environment_pill=f"Service: IBM watsonx")

    page = S.st.session_state[S.K_PAGE]
    render_fn = PAGES.get(page, pages_home.render)
    render_fn()


if __name__ == "__main__":
    main()
