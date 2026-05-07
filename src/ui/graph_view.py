"""Plotly visualization of the cybersecurity career graph."""
from __future__ import annotations

import math

import plotly.graph_objects as go

from ..data import DOMAINS, ROLES


def build_graph_figure(highlight_domain: str | None = None, highlight_role: str | None = None) -> go.Figure:
    # Place domains around an outer ring; their roles around an inner ring per domain.
    n_domains = len(DOMAINS)
    domain_radius = 1.0
    role_radius = 0.42

    positions: dict[str, tuple[float, float]] = {}
    for i, d in enumerate(DOMAINS):
        angle = 2 * math.pi * i / n_domains
        positions[d["id"]] = (domain_radius * math.cos(angle), domain_radius * math.sin(angle))

    # roles clustered around their parent domain
    for d in DOMAINS:
        roles = [r for r in ROLES if r["domain_id"] == d["id"]]
        cx, cy = positions[d["id"]]
        # offset cluster center outward a bit
        for j, r in enumerate(roles):
            inner_angle = 2 * math.pi * j / max(1, len(roles))
            positions[r["id"]] = (
                cx + role_radius * 0.55 * math.cos(inner_angle),
                cy + role_radius * 0.55 * math.sin(inner_angle),
            )

    edge_x: list[float] = []
    edge_y: list[float] = []
    for r in ROLES:
        x0, y0 = positions[r["domain_id"]]
        x1, y1 = positions[r["id"]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(color="rgba(160,170,200,0.25)", width=1),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # domain nodes
    fig.add_trace(
        go.Scatter(
            x=[positions[d["id"]][0] for d in DOMAINS],
            y=[positions[d["id"]][1] for d in DOMAINS],
            mode="markers+text",
            text=[d["name"] for d in DOMAINS],
            textposition="top center",
            textfont=dict(color="#e6edf6", size=12),
            marker=dict(
                size=[36 if d["id"] == highlight_domain else 26 for d in DOMAINS],
                color=[d["color"] for d in DOMAINS],
                line=dict(
                    color=["#22d3ee" if d["id"] == highlight_domain else "rgba(255,255,255,0.25)" for d in DOMAINS],
                    width=[3 if d["id"] == highlight_domain else 1 for d in DOMAINS],
                ),
                opacity=0.95,
            ),
            hovertext=[f"<b>{d['name']}</b><br>{d['blurb']}" for d in DOMAINS],
            hoverinfo="text",
            name="Domains",
        )
    )

    # role nodes
    role_colors = []
    role_sizes = []
    role_texts = []
    role_hovers = []
    for r in ROLES:
        is_focus = r["id"] == highlight_role
        role_colors.append("#f9fafb" if is_focus else "rgba(230,237,246,0.65)")
        role_sizes.append(20 if is_focus else 12)
        role_texts.append(r["name"] if is_focus else "")
        role_hovers.append(
            f"<b>{r['name']}</b><br>{r['summary']}<br>"
            f"<i>Seniority:</i> {r['seniority']}<br>"
            f"<i>Pay (US):</i> {r['salary_band_us']}"
        )
    fig.add_trace(
        go.Scatter(
            x=[positions[r["id"]][0] for r in ROLES],
            y=[positions[r["id"]][1] for r in ROLES],
            mode="markers+text",
            text=role_texts,
            textposition="bottom center",
            textfont=dict(color="#e6edf6", size=11),
            marker=dict(size=role_sizes, color=role_colors, line=dict(color="rgba(255,255,255,0.35)", width=1)),
            hovertext=role_hovers,
            hoverinfo="text",
            name="Roles",
        )
    )

    fig.update_layout(
        height=560,
        showlegend=False,
        margin=dict(l=8, r=8, t=8, b=8),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, range=[-1.6, 1.6]),
        yaxis=dict(visible=False, range=[-1.4, 1.4], scaleanchor="x", scaleratio=1),
    )
    return fig
