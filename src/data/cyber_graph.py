"""Cybersecurity career navigation graph.

This is a curated, opinionated map of the field — domains → roles → skills →
evidence — drawn from public references (NIST NICE Framework categories,
DHS/CISA workforce roles, common industry job titles). It powers the
explore/visualize features and grounds the agents so they don't fabricate
roles that don't exist.
"""
from __future__ import annotations

from typing import TypedDict


class DomainSpec(TypedDict):
    id: str
    name: str
    blurb: str
    color: str


class RoleSpec(TypedDict):
    id: str
    name: str
    domain_id: str
    seniority: str  # "entry" | "mid" | "senior"
    summary: str
    core_skills: list[str]
    typical_employers: list[str]
    salary_band_us: str


DOMAINS: list[DomainSpec] = [
    {
        "id": "soc",
        "name": "Security Operations (SOC)",
        "blurb": "Detect, triage, and respond to threats in real time.",
        "color": "#22d3ee",
    },
    {
        "id": "grc",
        "name": "Governance, Risk & Compliance (GRC)",
        "blurb": "Translate regulations and risk into policies and controls.",
        "color": "#a78bfa",
    },
    {
        "id": "appsec",
        "name": "Application Security (AppSec)",
        "blurb": "Find and fix flaws in software before attackers do.",
        "color": "#f472b6",
    },
    {
        "id": "offensive",
        "name": "Offensive Security",
        "blurb": "Simulate adversaries to harden defenses.",
        "color": "#f97316",
    },
    {
        "id": "cloud",
        "name": "Cloud Security",
        "blurb": "Secure the public cloud — identities, workloads, networks, data.",
        "color": "#34d399",
    },
    {
        "id": "iam",
        "name": "Identity & Access Management (IAM)",
        "blurb": "Make sure the right humans and machines have the right access.",
        "color": "#fbbf24",
    },
    {
        "id": "dfir",
        "name": "Digital Forensics & Incident Response (DFIR)",
        "blurb": "Investigate breaches, recover state, and tell the story.",
        "color": "#ef4444",
    },
    {
        "id": "engineering",
        "name": "Security Engineering",
        "blurb": "Build the controls, pipelines, and tooling that scale security.",
        "color": "#60a5fa",
    },
]


ROLES: list[RoleSpec] = [
    {
        "id": "soc_t1",
        "name": "SOC Analyst (Tier 1)",
        "domain_id": "soc",
        "seniority": "entry",
        "summary": "First responder for security alerts: triage, escalate, document.",
        "core_skills": ["Log analysis", "EDR/SIEM basics", "MITRE ATT&CK", "Incident write-ups"],
        "typical_employers": ["MSSPs", "Banks", "Health systems", "Mid-market in-house SOCs"],
        "salary_band_us": "$55k–$80k",
    },
    {
        "id": "soc_t2",
        "name": "SOC Analyst (Tier 2)",
        "domain_id": "soc",
        "seniority": "mid",
        "summary": "Owns deeper investigations and pivots from alerts to incidents.",
        "core_skills": ["Threat hunting", "Detection logic", "Forensic triage", "Tooling: Splunk/Sentinel"],
        "typical_employers": ["Enterprises", "MSSPs", "Critical infrastructure"],
        "salary_band_us": "$80k–$115k",
    },
    {
        "id": "detection_eng",
        "name": "Detection Engineer",
        "domain_id": "soc",
        "seniority": "mid",
        "summary": "Authors and tunes the detections the SOC actually trusts.",
        "core_skills": ["Sigma/KQL/SPL", "ATT&CK mapping", "Data engineering basics", "Test-driven detections"],
        "typical_employers": ["Tech companies", "Mature enterprise SOCs"],
        "salary_band_us": "$110k–$160k",
    },
    {
        "id": "ir",
        "name": "Incident Responder",
        "domain_id": "dfir",
        "seniority": "mid",
        "summary": "Leads response when something is on fire — scope, contain, eradicate.",
        "core_skills": ["Forensics", "Memory analysis", "Cloud IR", "Crisis communication"],
        "typical_employers": ["IR consulting (Mandiant, CrowdStrike)", "Large enterprises"],
        "salary_band_us": "$110k–$170k",
    },
    {
        "id": "forensics",
        "name": "Digital Forensics Analyst",
        "domain_id": "dfir",
        "seniority": "entry",
        "summary": "Collects and analyzes evidence from disks, memory, and the cloud.",
        "core_skills": ["Disk/memory forensics", "Chain of custody", "Autopsy/Volatility", "Report writing"],
        "typical_employers": ["Law firms", "Government", "DFIR consultancies"],
        "salary_band_us": "$70k–$105k",
    },
    {
        "id": "grc_analyst",
        "name": "GRC Analyst",
        "domain_id": "grc",
        "seniority": "entry",
        "summary": "Maps controls to frameworks (SOC 2, ISO 27001, NIST CSF) and tracks risk.",
        "core_skills": ["NIST CSF", "Risk registers", "Audit prep", "Stakeholder writing"],
        "typical_employers": ["SaaS companies", "Healthcare", "Financial services"],
        "salary_band_us": "$65k–$95k",
    },
    {
        "id": "compliance_mgr",
        "name": "Compliance Manager",
        "domain_id": "grc",
        "seniority": "mid",
        "summary": "Owns external audits, vendor risk, and regulatory mappings end-to-end.",
        "core_skills": ["SOC 2/ISO 27001", "Vendor risk", "Policy authoring", "Audit operations"],
        "typical_employers": ["Public companies", "Regulated industries"],
        "salary_band_us": "$110k–$155k",
    },
    {
        "id": "appsec_eng",
        "name": "Application Security Engineer",
        "domain_id": "appsec",
        "seniority": "mid",
        "summary": "Partners with devs on threat models, code review, and SDLC controls.",
        "core_skills": ["OWASP Top 10", "Threat modeling", "SAST/DAST", "Secure code review"],
        "typical_employers": ["Tech", "Fintech", "Health tech"],
        "salary_band_us": "$130k–$190k",
    },
    {
        "id": "pentester",
        "name": "Penetration Tester",
        "domain_id": "offensive",
        "seniority": "mid",
        "summary": "Performs authorized attacks against networks, apps, and cloud.",
        "core_skills": ["Web/network exploitation", "Burp Suite", "AD attacks", "Reporting"],
        "typical_employers": ["Consulting firms", "Internal red teams"],
        "salary_band_us": "$95k–$155k",
    },
    {
        "id": "red_teamer",
        "name": "Red Team Operator",
        "domain_id": "offensive",
        "seniority": "senior",
        "summary": "Long-running adversary emulation focused on detection-evasion-aware ops.",
        "core_skills": ["C2 frameworks", "OPSEC", "Custom tooling", "TTP development"],
        "typical_employers": ["FAANG", "Defense", "Specialist consultancies"],
        "salary_band_us": "$160k–$240k",
    },
    {
        "id": "cloudsec_eng",
        "name": "Cloud Security Engineer",
        "domain_id": "cloud",
        "seniority": "mid",
        "summary": "Hardens AWS/Azure/GCP — identity, network, workload, and data layers.",
        "core_skills": ["IAM least privilege", "IaC scanning", "CSPM/CWPP", "Kubernetes security"],
        "typical_employers": ["Cloud-native companies", "Banks moving to cloud"],
        "salary_band_us": "$140k–$200k",
    },
    {
        "id": "iam_eng",
        "name": "IAM Engineer",
        "domain_id": "iam",
        "seniority": "mid",
        "summary": "Designs SSO, MFA, lifecycle, and machine-identity systems.",
        "core_skills": ["SAML/OIDC", "Okta/Entra ID", "Zero trust", "Provisioning automation"],
        "typical_employers": ["Mid-to-large enterprises"],
        "salary_band_us": "$110k–$165k",
    },
    {
        "id": "sec_eng",
        "name": "Security Engineer (Generalist)",
        "domain_id": "engineering",
        "seniority": "mid",
        "summary": "Builds the platform that other security teams stand on.",
        "core_skills": ["Python/Go", "Terraform", "CI/CD security", "Detection-as-code"],
        "typical_employers": ["Tech companies", "Scale-ups"],
        "salary_band_us": "$140k–$210k",
    },
    {
        "id": "junior_sec_eng",
        "name": "Junior Security Engineer",
        "domain_id": "engineering",
        "seniority": "entry",
        "summary": "Apprentice role for engineers entering security with strong code skills.",
        "core_skills": ["Scripting", "Cloud basics", "Linux", "Reading PRs critically"],
        "typical_employers": ["Tech-forward companies with apprenticeship tracks"],
        "salary_band_us": "$95k–$130k",
    },
]


SKILL_GROUPS: dict[str, list[str]] = {
    "Foundations": [
        "Networking (TCP/IP, DNS, HTTP)",
        "Operating systems (Linux, Windows internals)",
        "Scripting (Python or PowerShell)",
        "Cloud literacy (AWS or Azure)",
    ],
    "Defensive": [
        "SIEM (Splunk / Sentinel / ELK)",
        "EDR telemetry & Sysmon",
        "Threat hunting with ATT&CK",
        "Incident triage & write-ups",
    ],
    "Offensive": [
        "Web exploitation (OWASP)",
        "Network exploitation",
        "Active Directory attacks",
        "Reporting findings clearly",
    ],
    "Engineering": [
        "Infrastructure-as-code (Terraform)",
        "CI/CD pipelines",
        "Detection-as-code (Sigma)",
        "Secure coding habits",
    ],
    "Governance": [
        "NIST CSF / ISO 27001 / SOC 2",
        "Risk registers & quantification",
        "Policy & control writing",
        "Audit operations",
    ],
}


EVIDENCE_BY_ROLE: dict[str, list[str]] = {
    "soc_t1": [
        "10+ TryHackMe SOC L1 rooms with public write-ups",
        "Home-lab Splunk dashboard repo with Sysmon-instrumented host",
        "CompTIA Security+ certification",
        "3 incident-report writing samples",
    ],
    "soc_t2": [
        "Threat-hunt write-up against a public dataset (e.g., MITRE CASCADE)",
        "Authored 3+ Sigma rules with documented test cases",
        "BTL1 or CySA+ certification",
        "Internal mentorship of Tier-1 colleagues (proof: write-ups)",
    ],
    "detection_eng": [
        "Open-source detections published (Sigma rules) on GitHub",
        "Blog post on detection engineering methodology",
        "CI/CD pipeline for detection deployment",
    ],
    "ir": [
        "Public IR scenario walkthroughs (BTL1 Investigations)",
        "GCFA or GCIH certification",
        "Memory-forensics write-up using Volatility",
    ],
    "forensics": [
        "Autopsy/Volatility lab write-ups",
        "GCFE or GCFA certification",
        "A practiced chain-of-custody report sample",
    ],
    "grc_analyst": [
        "Mock SOC 2 readiness assessment for a fictional SaaS",
        "Risk register sample showing 10+ risks with mitigations",
        "ISC2 CC certification (free, entry-level)",
    ],
    "compliance_mgr": [
        "Track record leading at least one external audit",
        "CISA or CRISC certification",
        "Vendor-risk program write-up",
    ],
    "appsec_eng": [
        "Threat-model document for an open-source app",
        "Public bug-bounty disclosures or HackTheBox AppSec rooms",
        "OSWE or eWPTX certification (advanced)",
    ],
    "pentester": [
        "PNPT, OSCP, or CRTP certification",
        "Public CTF write-ups (Hack The Box, TryHackMe)",
        "Sample pentest report (sanitized)",
    ],
    "red_teamer": [
        "OSCP + CRTO/Red Team Ops certification",
        "Custom tooling on GitHub",
        "Conference talk or detailed blog on TTPs",
    ],
    "cloudsec_eng": [
        "Hardened reference Terraform repo on GitHub",
        "AWS Security Specialty or AZ-500 certification",
        "Write-up of a multi-account guardrail rollout",
    ],
    "iam_eng": [
        "Okta/Entra demo tenant with SSO + lifecycle workflows",
        "Zero-trust architecture diagram + rationale",
        "Identity Management Institute certification (or vendor cert)",
    ],
    "sec_eng": [
        "Detection-as-code repo with CI",
        "Open-source security tooling contribution",
        "System design write-up (e.g., 'designing our secrets pipeline')",
    ],
    "junior_sec_eng": [
        "Strong general-engineering portfolio (open-source PRs, side projects)",
        "Security-flavored side project (e.g., small SAST tool)",
        "Security+ or ISC2 CC + AWS Cloud Practitioner",
    ],
}


# -----------------------------------------------------------------------------
# Lookup helpers
# -----------------------------------------------------------------------------


def list_domains() -> list[DomainSpec]:
    return list(DOMAINS)


def list_roles(domain_id: str | None = None) -> list[RoleSpec]:
    if domain_id is None:
        return list(ROLES)
    return [r for r in ROLES if r["domain_id"] == domain_id]


def domain_detail(domain_id: str) -> DomainSpec | None:
    for d in DOMAINS:
        if d["id"] == domain_id:
            return d
    return None


def role_detail(role_id: str) -> RoleSpec | None:
    for r in ROLES:
        if r["id"] == role_id:
            return r
    return None


def role_to_domain(role_id: str) -> DomainSpec | None:
    role = role_detail(role_id)
    return domain_detail(role["domain_id"]) if role else None


def edges() -> list[tuple[str, str]]:
    """(domain_id, role_id) tuples for graph drawing."""
    return [(r["domain_id"], r["id"]) for r in ROLES]
