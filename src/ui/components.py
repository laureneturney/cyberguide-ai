"""Reusable UI fragments — keep page files thin and readable.

Important rendering note:
    Streamlit's markdown parser follows CommonMark, which closes a raw-HTML
    block at the first blank line and treats 4-space-indented content as a
    code block. f-strings with multi-line, indented HTML look pretty in
    source but break in production (raw tags get rendered as text). Every
    helper below emits HTML as a single line via the `_render_html` shim.
"""
from __future__ import annotations

import html
from typing import Iterable

import streamlit as st


def _render_html(markup: str) -> None:
    """Render raw HTML, bypassing the markdown parser entirely.

    `st.html` was added in Streamlit 1.33 specifically for this case — it
    inserts the markup straight into the DOM, so CommonMark's HTML-block /
    indented-code-block rules never apply. We fall back to `st.markdown`
    only on the off chance an older Streamlit is in play.
    """
    if hasattr(st, "html"):
        st.html(markup)
    else:
        cleaned = "".join(line.strip() for line in markup.splitlines() if line.strip())
        st.markdown(cleaned, unsafe_allow_html=True)


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
    tags_row = f'<div class="cg-tags-row">{tag_html}</div>' if tag_html else ""
    body_block = f'<div class="why">{body_html}</div>' if body_html else ""
    _render_html(
        f'<div class="cg-card">'
        f'<h4>{html.escape(title)}</h4>'
        f'{meta_html}{tags_row}{body_block}'
        f'</div>'
    )


def step(
    idx: int,
    title: str,
    week_range: str,
    objectives: list[str],
    evidence: str,
    rationale: str,
) -> None:
    obj_items = "".join(f"<li>{html.escape(o)}</li>" for o in objectives)
    _render_html(
        f'<div class="cg-step">'
        f'<div class="num">{idx}</div>'
        f'<div style="flex:1">'
        f'<h4>{html.escape(title)}'
        f' <span class="cg-tag info">Weeks {html.escape(week_range)}</span></h4>'
        f'<ul style="margin: 6px 0 0 18px; padding:0;">{obj_items}</ul>'
        f'<div style="margin-top:8px; font-size:12px; color: var(--cg-muted);">'
        f'<strong>Evidence:</strong> {html.escape(evidence)}'
        f'</div>'
        f'<div class="why">Why now: {html.escape(rationale)}</div>'
        f'</div>'
        f'</div>'
    )


def pill(text: str, kind: str = "info") -> str:
    return f'<span class="cg-tag {kind}">{html.escape(text)}</span>'


def chat_bubble(role: str, content: str) -> None:
    cls = "user" if role == "user" else "assistant"
    safe = html.escape(content).replace("\n", "<br/>")
    _render_html(f'<div class="cg-bubble {cls}">{safe}</div>')


def section_header(title: str, sub: str = "") -> None:
    sub_html = (
        f'<div class="cg-muted" style="font-size:13px; margin-top:-4px;">{html.escape(sub)}</div>'
        if sub
        else ""
    )
    _render_html(
        f'<div style="margin: 6px 0 12px 0;">'
        f'<h2 style="margin-bottom:2px;">{html.escape(title)}</h2>'
        f'{sub_html}'
        f'</div>'
    )


def empty_state(text: str, action_label: str = "", on_action_key: str | None = None) -> bool:
    _render_html(
        f'<div class="cg-card" style="text-align:center; padding: 28px;">'
        f'<div style="font-size:14px; color: var(--cg-muted);">{html.escape(text)}</div>'
        f'</div>'
    )
    if action_label and on_action_key:
        return st.button(action_label, key=on_action_key)
    return False
