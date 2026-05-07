"""Static, audit-friendly knowledge sources used by the agents.

We keep these as plain Python so the app is self-contained — no external DB,
no LLM hallucinations for the parts of the system that need to be deterministic.
"""
from .cyber_graph import (
    DOMAINS,
    ROLES,
    EVIDENCE_BY_ROLE,
    SKILL_GROUPS,
    list_domains,
    list_roles,
    role_detail,
    domain_detail,
    role_to_domain,
    edges,
)
from .resources import CURATED_RESOURCES, resources_for

__all__ = [
    "DOMAINS",
    "ROLES",
    "EVIDENCE_BY_ROLE",
    "SKILL_GROUPS",
    "list_domains",
    "list_roles",
    "role_detail",
    "domain_detail",
    "role_to_domain",
    "edges",
    "CURATED_RESOURCES",
    "resources_for",
]
