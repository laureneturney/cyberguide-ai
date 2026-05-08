"""Roadmap — the single conversational entry point.

Flow:
  1. User describes their career goals in their own words (and / or uploads
     a resume), tunes a few sliders (hours, timeline, budget), and clicks
     "Build my roadmap".
  2. The orchestrator routes the text through the Resume Profiler agent to
     extract skills + suggested role + domain, builds a UserProfile, and
     hands it to the Pathfinder for a personalized plan.
  3. Below the plan, a "Talk to the Pathfinder" chat lets the user refine
     the plan in plain language and re-plan with a single click.
"""
from __future__ import annotations

import html as _html

import streamlit as st

from ..data import DOMAINS, ROLES, domain_detail, role_detail
from ..tools import parse_paste, parse_upload
from . import state as S
from .components import card, chat_bubble, empty_state, section_header, step, _render_html


# -----------------------------------------------------------------------------
# Plan generation
# -----------------------------------------------------------------------------


def _build_plan(*, goals_text: str, resume_text: str, hours: int, weeks: int,
                budget: int, domain_id: str, role_id: str, name: str) -> None:
    try:
        with st.spinner("Pathfinder agent is reading your goals and drafting a plan…"):
            profile, analysis = S.orch().build_profile_from_inputs(
                goals_text=goals_text,
                resume_text=resume_text,
                weekly_hours=hours,
                timeline_weeks=weeks,
                budget_usd=budget,
                domain_id=domain_id,
                role_id=role_id,
                name=name,
            )
            S.set_profile(profile)
            S.st.session_state[S.K_RESUME_ANALYSIS] = analysis.model_dump()
            plan = S.orch().make_plan(profile)
            S.st.session_state[S.K_PLAN] = plan
            S.st.session_state[S.K_MILESTONE_PROGRESS] = {
                i: False for i in range(len(plan.milestones))
            }
            S.st.session_state[S.K_PATHFINDER_CHAT] = []  # fresh thread per plan
    except Exception as exc:  # noqa: BLE001
        st.error(f"Couldn't build the roadmap: {exc}")
        return
    st.toast("Roadmap built — scroll down to review it.", icon="✨")
    st.rerun()


def _replan_with_message(refinement: str) -> None:
    """Re-plan from the current profile + an in-line refinement note."""
    p = S.profile()
    if refinement.strip():
        # Lift the refinement into the constraints field so the agent sees it.
        merged = (p.constraints + ". " if p.constraints else "") + refinement.strip()
        p = p.model_copy(update={"constraints": merged.strip(". ").strip()})
        S.set_profile(p)
    try:
        with st.spinner("Re-planning with your refinement…"):
            plan = S.orch().make_plan(p)
            S.st.session_state[S.K_PLAN] = plan
            S.st.session_state[S.K_MILESTONE_PROGRESS] = {
                i: False for i in range(len(plan.milestones))
            }
    except Exception as exc:  # noqa: BLE001
        st.error(f"Re-plan failed: {exc}")
        return
    st.toast("Plan updated.", icon="🔄")


# -----------------------------------------------------------------------------
# Goal-input section
# -----------------------------------------------------------------------------


def _render_goal_input(has_plan: bool) -> None:
    section_header(
        "Build your roadmap" if not has_plan else "Update your roadmap",
        "Tell the Pathfinder about your goals, background, time, and budget.",
    )

    p_existing = S.profile()

    goals_text = st.text_area(
        "Your goals, in your own words",
        value=S.st.session_state.get(S.K_GOALS_TEXT, ""),
        height=160,
        placeholder=(
            "e.g.\n"
            "I'm a 3rd-year history teacher pivoting to cybersecurity. I have 6 hours a week, want "
            "to land a SOC analyst role within 5 months, and can spend about $400 on certifications. "
            "I've finished Networking Essentials on Cisco and built a small home lab."
        ),
        key="roadmap_goals_input",
    )

    with st.expander("Optional: upload a resume (PDF / DOCX / TXT)", expanded=False):
        uploaded = st.file_uploader(
            "Drop a resume — we'll merge its skills/certs into your roadmap inputs.",
            type=["pdf", "docx", "txt", "md"],
            key="roadmap_resume_upload",
        )
        resume_text = ""
        if uploaded is not None:
            parsed = parse_upload(uploaded.name, uploaded.getvalue())
            if parsed.text:
                resume_text = parsed.text
                st.success(
                    f"Parsed {parsed.source.upper()}: {parsed.char_count:,} characters extracted.",
                    icon="✅",
                )
            else:
                st.error(f"Couldn't extract text — {parsed.notes or 'try pasting into the goals box.'}")
        S.st.session_state[S.K_RESUME_TEXT] = resume_text or S.st.session_state.get(S.K_RESUME_TEXT, "")

    with st.expander("Optional: fine-tune time, budget, and target role", expanded=not has_plan):
        c1, c2, c3 = st.columns(3)
        with c1:
            hours = st.slider("Weekly hours", 2, 30, p_existing.weekly_hours or 8)
        with c2:
            weeks = st.slider("Timeline (weeks)", 4, 52, p_existing.timeline_weeks or 16)
        with c3:
            budget = st.number_input(
                "Budget (USD)",
                min_value=0,
                max_value=10000,
                value=p_existing.budget_usd or 500,
                step=50,
            )
        c4, c5, c6 = st.columns(3)
        with c4:
            name = st.text_input("Name (optional)", value=p_existing.name)
        with c5:
            d_options = {"": "— let the agent decide —"} | {d["id"]: d["name"] for d in DOMAINS}
            d_keys = list(d_options.keys())
            d_index = d_keys.index(p_existing.preferred_domain) if p_existing.preferred_domain in d_options else 0
            domain_id = st.selectbox(
                "Domain (optional)",
                options=d_keys,
                format_func=lambda k: d_options[k],
                index=d_index,
            )
        with c6:
            roles_in_scope = [r for r in ROLES if not domain_id or r["domain_id"] == domain_id]
            r_options = {"": "— let the agent decide —"} | {r["id"]: r["name"] for r in roles_in_scope}
            r_keys = list(r_options.keys())
            r_index = r_keys.index(p_existing.target_role) if p_existing.target_role in r_options else 0
            role_id = st.selectbox(
                "Role (optional)",
                options=r_keys,
                format_func=lambda k: r_options[k],
                index=r_index,
            )

    btn_label = "🚀 Build my roadmap" if not has_plan else "🔄 Rebuild with these inputs"
    if st.button(btn_label, use_container_width=True, type="primary", key="roadmap_build_btn"):
        S.st.session_state[S.K_GOALS_TEXT] = goals_text or ""
        if not (goals_text.strip() or resume_text.strip() or domain_id or role_id):
            st.warning("Tell the agent something about your goals — even a sentence helps.")
            return
        _build_plan(
            goals_text=goals_text or "",
            resume_text=resume_text,
            hours=int(hours),
            weeks=int(weeks),
            budget=int(budget),
            domain_id=domain_id,
            role_id=role_id,
            name=name,
        )


# -----------------------------------------------------------------------------
# Plan display + Pathfinder chat
# -----------------------------------------------------------------------------


def _render_inferred_chip() -> None:
    p = S.profile()
    domain_name = (domain_detail(p.preferred_domain) or {}).get("name", "—")
    role_name = (role_detail(p.target_role) or {}).get("name", "—")
    bits = [
        ("Domain", domain_name),
        ("Role", role_name),
        ("Hours/wk", str(p.weekly_hours)),
        ("Timeline", f"{p.timeline_weeks} wks"),
        ("Budget", f"${p.budget_usd}"),
    ]
    items = "".join(
        f'<span class="cg-tag info"><b>{_html.escape(k)}</b>&nbsp;<span style="opacity:.85;">{_html.escape(v)}</span></span>'
        for k, v in bits
    )
    _render_html(
        f'<div style="display:flex; flex-wrap:wrap; gap:6px; margin: 4px 0 14px 0;">{items}</div>'
    )


def _render_plan() -> None:
    plan = S.st.session_state[S.K_PLAN]

    section_header("Your personalized roadmap", "Generated by the Pathfinder agent based on what you told us.")
    _render_inferred_chip()

    card(
        "Plan summary",
        f"<span class='cg-muted'>{_html.escape(plan.summary)}</span>"
        + (f"<br><br><b>Next action:</b> {_html.escape(plan.next_action)}" if plan.next_action else ""),
        tags=[("watsonx", "info"), (f"{len(plan.milestones)} milestones", "ok")],
    )

    progress = S.st.session_state[S.K_MILESTONE_PROGRESS]
    if plan.milestones:
        done = sum(1 for v in progress.values() if v)
        st.progress(
            done / max(1, len(plan.milestones)),
            text=f"{done} / {len(plan.milestones)} milestones marked complete",
        )

    for i, m in enumerate(plan.milestones, 1):
        step(i, m.title, m.week_range, m.objectives, m.evidence, m.rationale)
        checked = st.checkbox(
            f"Mark Milestone {i} complete",
            value=progress.get(i - 1, False),
            key=f"ms_done_{i-1}",
        )
        progress[i - 1] = checked

    if plan.risks:
        risks_html = "<ul style='margin: 4px 0 0 18px;'>" + "".join(
            f"<li>{_html.escape(r)}</li>" for r in plan.risks
        ) + "</ul>"
        card("Risks the agent flagged", risks_html, tags=[("Be aware", "warn")])


def _render_pathfinder_chat() -> None:
    section_header(
        "Talk to the Pathfinder about your plan",
        "Ask follow-ups, push back, or describe a change — the agent can re-plan in line.",
    )

    history = S.st.session_state[S.K_PATHFINDER_CHAT]
    if not history:
        _render_html(
            '<div class="cg-card">'
            "<b>Try one of these:</b><br>"
            '<span class="cg-muted">'
            "• &ldquo;Why this cert and not Sec+ first?&rdquo;<br>"
            "• &ldquo;I just dropped to 4 hrs/wk — re-plan.&rdquo;<br>"
            "• &ldquo;What's the smallest first thing I can do this weekend?&rdquo;"
            "</span></div>"
        )

    for role, content in history:
        chat_bubble(role, content)

    user_msg = st.chat_input("Ask the Pathfinder…", key="pathfinder_chat_input")
    if user_msg:
        _ask_pathfinder(user_msg)


def _ask_pathfinder(user_msg: str) -> None:
    p = S.profile()
    plan = S.st.session_state[S.K_PLAN]
    history: list[tuple[str, str]] = S.st.session_state[S.K_PATHFINDER_CHAT]

    # Inject a one-time context message describing the current plan so the
    # generic chat agent answers in-context. We don't store this in history
    # so the user only sees their own messages and the agent's replies.
    plan_context = ""
    if plan is not None:
        ms = "; ".join(f"Wk {m.week_range}: {m.title}" for m in plan.milestones)
        plan_context = (
            f"Current plan summary: {plan.summary}\n"
            f"Milestones: {ms}\n"
            f"Risks: {' / '.join(plan.risks)}\n"
            f"Next action: {plan.next_action}"
        )
    seeded = list(history)
    if plan_context:
        seeded.insert(0, ("system", plan_context))

    try:
        with st.spinner("Pathfinder is thinking…"):
            reply = S.orch().chat(p, seeded, user_msg)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Chat error: {exc}")
        return

    history.append(("user", user_msg))
    history.append(("assistant", reply))

    # Heuristic: if the user said something that sounds like a re-plan ask,
    # call the pathfinder right after replying so the plan visibly updates.
    triggers = ("re-plan", "replan", "rebuild", "update the plan", "re plan",
                "switch to", "i changed", "i want to switch", "let's switch")
    if any(t in user_msg.lower() for t in triggers):
        _replan_with_message(user_msg)
    st.rerun()


# -----------------------------------------------------------------------------
# Top-level render
# -----------------------------------------------------------------------------


def render() -> None:
    plan = S.st.session_state[S.K_PLAN]
    has_plan = plan is not None

    _render_goal_input(has_plan=has_plan)
    _render_html('<div class="cg-divider"></div>')

    if not has_plan:
        empty_state("No roadmap yet — tell the agent your goals above and click Build my roadmap.")
        return

    _render_plan()
    _render_html('<div class="cg-divider"></div>')
    _render_pathfinder_chat()
