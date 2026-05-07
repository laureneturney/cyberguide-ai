"""Centralizes session-state initialization.

Streamlit re-runs the script on every interaction, so anything we want to
persist within the demo session has to live in `st.session_state`. We keep
the keys here so the UI files don't sprinkle string literals everywhere.
"""
from __future__ import annotations

import streamlit as st

from ..agents import Orchestrator, UserProfile


# Keys
K_PROFILE = "cg_profile"
K_PLAN = "cg_plan"
K_DECISIONS = "cg_decisions"  # list of (request, result)
K_CHAT = "cg_chat"  # list of (role, content)
K_RESOURCES = "cg_resources"  # last retrieval
K_ORCH = "cg_orchestrator"
K_PAGE = "cg_page"
K_MILESTONE_PROGRESS = "cg_milestone_progress"  # dict[milestone_idx] -> bool
K_RESUME_ANALYSIS = "cg_resume_analysis"  # last ResumeAnalysis (dict-serialized)
K_RESUME_TEXT = "cg_resume_text"  # last parsed resume text (for re-analysis)


def ensure_state() -> None:
    if K_ORCH not in st.session_state:
        st.session_state[K_ORCH] = Orchestrator()
    if K_PROFILE not in st.session_state:
        st.session_state[K_PROFILE] = UserProfile()
    if K_PLAN not in st.session_state:
        st.session_state[K_PLAN] = None
    if K_DECISIONS not in st.session_state:
        st.session_state[K_DECISIONS] = []
    if K_CHAT not in st.session_state:
        st.session_state[K_CHAT] = []
    if K_RESOURCES not in st.session_state:
        st.session_state[K_RESOURCES] = []
    if K_PAGE not in st.session_state:
        st.session_state[K_PAGE] = "Home"
    if K_MILESTONE_PROGRESS not in st.session_state:
        st.session_state[K_MILESTONE_PROGRESS] = {}
    if K_RESUME_ANALYSIS not in st.session_state:
        st.session_state[K_RESUME_ANALYSIS] = None
    if K_RESUME_TEXT not in st.session_state:
        st.session_state[K_RESUME_TEXT] = ""


def reset_session() -> None:
    keep = set()
    for k in list(st.session_state.keys()):
        if k.startswith("cg_") and k not in keep:
            del st.session_state[k]
    ensure_state()


def orch() -> Orchestrator:
    return st.session_state[K_ORCH]


def profile() -> UserProfile:
    return st.session_state[K_PROFILE]


def set_profile(p: UserProfile) -> None:
    st.session_state[K_PROFILE] = p
