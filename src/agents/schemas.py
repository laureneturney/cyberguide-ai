"""Typed shapes shared across agents and the UI.

Pydantic gives us validation + JSON-friendly serialization for free, which
matters when LLM output gets coerced into structured plans/decisions.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    name: str = ""
    background: str = ""  # e.g., "career changer from teaching"
    education: str = ""
    weekly_hours: int = 8
    timeline_weeks: int = 16
    budget_usd: int = 500
    constraints: str = ""  # free-text
    preferred_domain: str = ""  # domain id, e.g. "soc"
    target_role: str = ""  # role id, e.g. "soc_t1"
    skills_self_rated: dict[str, int] = Field(default_factory=dict)  # 1–5
    interests: list[str] = Field(default_factory=list)
    location: str = ""

    def is_minimal(self) -> bool:
        return bool(self.preferred_domain or self.target_role)


class Milestone(BaseModel):
    week_range: str
    title: str
    objectives: list[str]
    evidence: str
    rationale: str


class Plan(BaseModel):
    summary: str
    milestones: list[Milestone] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    next_action: str = ""
    generated_with: str = "IBM watsonx"
    rationale: str = ""


class DecisionRequest(BaseModel):
    question: str
    options: list[str] = Field(default_factory=list)
    context: str = ""


class DecisionOption(BaseModel):
    label: str
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    fit_score: float = 0.5


class DecisionResult(BaseModel):
    question: str
    options: list[DecisionOption]
    recommendation: str
    rationale: str
    confidence: float
    human_review_required: bool = True


class RetrievedResource(BaseModel):
    title: str
    kind: str
    url: str
    why: str
    cost: str = ""
    time_estimate: str = ""
    source: Literal["curated", "web", "mock"] = "curated"


class GraphExplanation(BaseModel):
    domain_overview: str
    key_roles: list[str]
    core_skills: list[str]
    evidence_employers_value: list[str]
    common_first_role: str


class ResumeAnalysis(BaseModel):
    summary: str
    background_label: str  # short, fit for UserProfile.background
    estimated_years_experience: float = 0.0
    education: str = ""
    skills_detected: dict[str, int] = Field(default_factory=dict)  # 1-5
    certifications: list[str] = Field(default_factory=list)
    courses: list[str] = Field(default_factory=list)
    suggested_domain_id: str = ""
    suggested_role_id: str = ""
    rationale: str = ""
    gaps_for_target: list[str] = Field(default_factory=list)
    confidence: float = 0.6
