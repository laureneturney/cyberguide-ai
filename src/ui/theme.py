"""Visual theme — IBM-flavored dark mode with cybersecurity neon accents.

We inject a single CSS block on every page render to override Streamlit's
default look without forking the framework. Keep selectors scoped narrowly
so future Streamlit upgrades don't silently break the styling.
"""
from __future__ import annotations

import streamlit as st


PRIMARY = "#0f62fe"  # IBM blue
ACCENT = "#22d3ee"   # cyber cyan
ACCENT_2 = "#a78bfa" # purple
BG_DEEP = "#08090d"
BG = "#0d111a"
BG_PANEL = "#121826"
BORDER = "#1f2a3d"
TEXT = "#e6edf6"
MUTED = "#8b97ad"
SUCCESS = "#34d399"
WARN = "#fbbf24"
DANGER = "#f87171"


def inject_css() -> None:
    st.markdown(
        f"""
<style>
    :root {{
        --cg-primary: {PRIMARY};
        --cg-accent: {ACCENT};
        --cg-accent-2: {ACCENT_2};
        --cg-bg: {BG};
        --cg-bg-deep: {BG_DEEP};
        --cg-panel: {BG_PANEL};
        --cg-border: {BORDER};
        --cg-text: {TEXT};
        --cg-muted: {MUTED};
    }}

    .stApp {{
        background:
            radial-gradient(900px 480px at 12% -10%, rgba(15,98,254,0.18), transparent 60%),
            radial-gradient(700px 420px at 110% 0%, rgba(167,139,250,0.18), transparent 60%),
            linear-gradient(180deg, {BG_DEEP} 0%, {BG} 100%) !important;
        color: {TEXT};
    }}
    [data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stSidebar"] > div:first-child {{
        background: linear-gradient(180deg, #0a0e18 0%, #0d111a 100%);
        border-right: 1px solid {BORDER};
    }}

    h1, h2, h3, h4 {{ color: {TEXT}; letter-spacing: -0.01em; }}

    /* Brand bar */
    .cg-brand {{
        display:flex; align-items:center; gap:14px;
        padding: 14px 18px; margin-bottom: 14px;
        border: 1px solid {BORDER};
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(15,98,254,0.16), rgba(34,211,238,0.10));
        backdrop-filter: blur(6px);
    }}
    .cg-brand .logo {{
        width:42px; height:42px; border-radius:10px;
        background: conic-gradient(from 220deg, {PRIMARY}, {ACCENT}, {ACCENT_2}, {PRIMARY});
        box-shadow: 0 8px 20px rgba(15,98,254,0.30), inset 0 0 0 2px rgba(255,255,255,0.12);
        position:relative;
    }}
    .cg-brand .logo::after {{
        content:""; position:absolute; inset:8px; border-radius:6px;
        background:#0b0f18; box-shadow: inset 0 0 0 1px rgba(255,255,255,0.08);
    }}
    .cg-brand .title {{ font-size: 22px; font-weight: 700; }}
    .cg-brand .sub {{ font-size: 12px; color: {MUTED}; }}
    .cg-brand .pill {{
        margin-left:auto; font-size: 11px;
        padding: 4px 10px; border-radius: 999px;
        background: rgba(34,211,238,0.10); color:{ACCENT};
        border: 1px solid rgba(34,211,238,0.32);
    }}

    .cg-card {{
        border: 1px solid {BORDER};
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)) {BG_PANEL};
        border-radius: 14px;
        padding: 18px 18px 14px;
        margin-bottom: 14px;
        box-shadow: 0 6px 24px rgba(0,0,0,0.25);
    }}
    .cg-card h4 {{ margin: 0 0 6px 0; font-size: 16px; }}
    .cg-card .meta {{ color: {MUTED}; font-size: 12px; }}
    .cg-card .why {{ color: {TEXT}; font-size: 13px; margin-top:6px; }}

    .cg-tag {{
        display:inline-block; padding: 2px 8px; font-size:11px; border-radius:999px;
        border:1px solid {BORDER}; color:{MUTED}; margin-right:6px; margin-top:4px;
    }}
    .cg-tag.ok {{ color:{SUCCESS}; border-color:rgba(52,211,153,0.35); }}
    .cg-tag.warn {{ color:{WARN}; border-color:rgba(251,191,36,0.35); }}
    .cg-tag.bad {{ color:{DANGER}; border-color:rgba(248,113,113,0.35); }}
    .cg-tag.info {{ color:{ACCENT}; border-color:rgba(34,211,238,0.35); }}

    .cg-step {{
        display:flex; gap: 14px; padding: 14px;
        border:1px solid {BORDER}; border-radius:12px;
        background: rgba(255,255,255,0.015); margin-bottom: 10px;
    }}
    .cg-step .num {{
        flex: 0 0 36px; height:36px; border-radius:50%;
        background: linear-gradient(135deg, {PRIMARY}, {ACCENT});
        display:flex; align-items:center; justify-content:center;
        font-weight:700; color:#04101a;
    }}
    .cg-step h4 {{ margin: 0 0 4px 0; }}
    .cg-step p, .cg-step li {{ color: {TEXT}; font-size:13px; }}
    .cg-step .why {{ color: {MUTED}; font-size:12px; margin-top:6px; font-style: italic; }}

    .cg-rec {{
        padding: 14px; border-radius: 12px;
        background: linear-gradient(135deg, rgba(52,211,153,0.10), rgba(34,211,238,0.06));
        border: 1px solid rgba(52,211,153,0.30);
        color: {TEXT};
    }}

    /* Buttons */
    .stButton > button {{
        background: linear-gradient(180deg, {PRIMARY}, #0050d4);
        color:#fff; border:0; border-radius:10px; font-weight:600;
        box-shadow: 0 6px 18px rgba(15,98,254,0.30);
    }}
    .stButton > button:hover {{
        filter: brightness(1.08);
        box-shadow: 0 6px 24px rgba(15,98,254,0.45);
    }}
    .stButton.cg-secondary > button {{
        background: rgba(255,255,255,0.05); color:{TEXT};
        border: 1px solid {BORDER}; box-shadow:none;
    }}

    /* Inputs */
    .stTextInput > div > div, .stTextArea textarea, .stNumberInput input,
    .stSelectbox > div > div, .stMultiSelect > div > div {{
        background: {BG_PANEL} !important; color: {TEXT} !important;
        border: 1px solid {BORDER} !important; border-radius: 10px !important;
    }}
    .stSlider [data-baseweb="slider"] > div > div {{ background: {ACCENT}; }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{ gap: 4px; }}
    .stTabs [data-baseweb="tab"] {{
        padding: 8px 14px; border-radius: 10px 10px 0 0;
        background: rgba(255,255,255,0.03);
        color: {MUTED};
    }}
    .stTabs [aria-selected="true"] {{
        background: {BG_PANEL} !important; color: {TEXT} !important;
        border: 1px solid {BORDER}; border-bottom-color: {BG_PANEL};
    }}

    /* Chat bubbles */
    .cg-bubble {{
        padding: 10px 14px; border-radius: 14px;
        max-width: 100%; margin: 4px 0;
        line-height: 1.45; font-size: 14px;
    }}
    .cg-bubble.user {{
        background: linear-gradient(135deg, rgba(15,98,254,0.16), rgba(15,98,254,0.06));
        border: 1px solid rgba(15,98,254,0.30);
    }}
    .cg-bubble.assistant {{
        background: rgba(255,255,255,0.03);
        border: 1px solid {BORDER};
    }}

    /* Misc */
    .cg-muted {{ color: {MUTED}; }}
    .cg-divider {{ height:1px; background:{BORDER}; margin: 12px 0; }}
    a, a:visited {{ color: {ACCENT}; }}
</style>
        """,
        unsafe_allow_html=True,
    )


def brand_bar(*, environment_pill: str | None = None) -> None:
    pill_html = ""
    if environment_pill:
        pill_html = f'<span class="pill">{environment_pill}</span>'
    st.markdown(
        f"""
<div class="cg-brand">
    <div class="logo"></div>
    <div>
        <div class="title">CyberGuide.AI</div>
        <div class="sub">Agentic career navigation for cybersecurity • powered by IBM watsonx</div>
    </div>
    {pill_html}
</div>
        """,
        unsafe_allow_html=True,
    )
