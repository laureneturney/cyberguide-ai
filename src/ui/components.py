"""Reusable UI fragments — keep page files thin and readable."""
from __future__ import annotations

import html
from typing import Iterable

import streamlit as st


def card(
    title: str,
    body_html: str = "",
    *,
    meta: str = "",
    tags: Iterable[tuple[str, str]] = (),
) -> None:
    tag_html = "".join(
        f'<span class="cg-tag {kind}">{html.escape(label)}</span>' for label, kind in tags
    )
    meta_html = f'<div class="meta">{html.escape(meta)}</div>' if meta else ""
    st.markdown(
        f"""
<div class="cg-card">
    <h4>{html.escape(title)}</h4>
    {meta_html}
    <div>{tag_html}</div>
    <div class="why">{body_html}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def step(idx: int, title: str, week_range: str, objectives: list[str], evidence: str, rationale: str) -> None:
    obj_items = "".join(f"<li>{html.escape(o)}</li>" for o in objectives)
    st.markdown(
        f"""
<div class="cg-step">
    <div class="num">{idx}</div>
    <div style="flex:1">
        <h4>{html.escape(title)}
            <span class="cg-tag info">Weeks {html.escape(week_range)}</span>
        </h4>
        <ul style="margin: 6px 0 0 18px; padding:0;">{obj_items}</ul>
        <div style="margin-top:8px; font-size:12px; color: var(--cg-muted);">
            <strong>Evidence:</strong> {html.escape(evidence)}
        </div>
        <div class="why">Why now: {html.escape(rationale)}</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def pill(text: str, kind: str = "info") -> str:
    return f'<span class="cg-tag {kind}">{html.escape(text)}</span>'


def chat_bubble(role: str, content: str) -> None:
    cls = "user" if role == "user" else "assistant"
    safe = html.escape(content).replace("\n", "<br/>")
    st.markdown(f'<div class="cg-bubble {cls}">{safe}</div>', unsafe_allow_html=True)


def section_header(title: str, sub: str = "") -> None:
    sub_html = f'<div class="cg-muted" style="font-size:13px; margin-top:-4px;">{html.escape(sub)}</div>' if sub else ""
    st.markdown(
        f'<div style="margin: 6px 0 12px 0;"><h2 style="margin-bottom:2px;">{html.escape(title)}</h2>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def empty_state(text: str, action_label: str = "", on_action_key: str | None = None) -> bool:
    st.markdown(
        f"""
<div class="cg-card" style="text-align:center; padding: 28px;">
    <div style="font-size:14px; color: var(--cg-muted);">{html.escape(text)}</div>
</div>
""",
        unsafe_allow_html=True,
    )
    if action_label and on_action_key:
        return st.button(action_label, key=on_action_key)
    return False
