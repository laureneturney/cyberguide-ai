"""CyberGuide.AI — Streamlit entry point.

Run locally:    streamlit run streamlit_app.py
Deploy on Streamlit Cloud: just point it at this file in the repo root.
"""
from __future__ import annotations

import streamlit as st

from src.config import settings
from src.ui import state as S
from src.ui.theme import inject_css, brand_bar
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
        st.markdown(
            f"""
<div style='padding:14px 8px 6px 8px;'>
  <div style='font-weight:700; font-size:18px;'>CyberGuide.AI</div>
  <div style='color:#8b97ad; font-size:11px; margin-top:2px;'>
      Powered by <b>IBM watsonx</b> · {S.orch().display_model}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
        for label in PAGES.keys():
            is_active = S.st.session_state[S.K_PAGE] == label
            btn_label = f"{'●  ' if is_active else '○  '}{label}"
            if st.button(btn_label, key=f"nav_{label}", use_container_width=True):
                S.st.session_state[S.K_PAGE] = label
                st.rerun()

        st.markdown('<div class="cg-divider"></div>', unsafe_allow_html=True)
        with st.expander("Session controls"):
            if st.button("🧹 Reset session", use_container_width=True):
                S.reset_session()
                st.rerun()
            st.caption("Session-only persistence — reloading the page clears the demo state.")

        st.markdown('<div class="cg-divider"></div>', unsafe_allow_html=True)
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
