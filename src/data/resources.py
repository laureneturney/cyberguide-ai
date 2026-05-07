"""Curated open and freely-available cybersecurity learning resources.

These are the offline-safe baseline. The retriever agent enriches them with
fresh web-search results when ENABLE_WEB_SEARCH=true.
"""
from __future__ import annotations

from typing import TypedDict


class Resource(TypedDict):
    title: str
    kind: str  # "course" | "lab" | "certification" | "reference" | "book" | "community"
    url: str
    why: str
    cost: str
    time_estimate: str
    role_ids: list[str]
    domain_ids: list[str]


CURATED_RESOURCES: list[Resource] = [
    {
        "title": "TryHackMe — SOC Level 1 Path",
        "kind": "lab",
        "url": "https://tryhackme.com/path/outline/soclevel1",
        "why": "Hands-on triage practice tuned to entry-level SOC interviews.",
        "cost": "$14/month",
        "time_estimate": "60–90 hrs",
        "role_ids": ["soc_t1", "soc_t2"],
        "domain_ids": ["soc", "dfir"],
    },
    {
        "title": "Blue Team Labs Online — Investigations",
        "kind": "lab",
        "url": "https://blueteamlabs.online/",
        "why": "Realistic SOC scenarios with reportable evidence.",
        "cost": "Free + paid tiers",
        "time_estimate": "self-paced",
        "role_ids": ["soc_t1", "soc_t2", "ir", "forensics"],
        "domain_ids": ["soc", "dfir"],
    },
    {
        "title": "CompTIA Security+ (SY0-701)",
        "kind": "certification",
        "url": "https://www.comptia.org/certifications/security",
        "why": "The most widely-asked-for entry-level cert in US listings.",
        "cost": "$392 exam",
        "time_estimate": "8–12 weeks",
        "role_ids": ["soc_t1", "junior_sec_eng", "grc_analyst"],
        "domain_ids": ["soc", "grc", "engineering"],
    },
    {
        "title": "ISC2 Certified in Cybersecurity (CC) — Free",
        "kind": "certification",
        "url": "https://www.isc2.org/certifications/cc",
        "why": "Free entry-level cert from a respected body — great résumé starter.",
        "cost": "Free (incl. exam)",
        "time_estimate": "2–4 weeks",
        "role_ids": ["soc_t1", "grc_analyst", "junior_sec_eng"],
        "domain_ids": ["soc", "grc", "engineering"],
    },
    {
        "title": "MITRE ATT&CK Navigator",
        "kind": "reference",
        "url": "https://mitre-attack.github.io/attack-navigator/",
        "why": "Shared adversary-tactic vocabulary every blue-team interview leans on.",
        "cost": "Free",
        "time_estimate": "ongoing",
        "role_ids": ["soc_t1", "soc_t2", "detection_eng", "ir"],
        "domain_ids": ["soc", "dfir"],
    },
    {
        "title": "PortSwigger Web Security Academy",
        "kind": "course",
        "url": "https://portswigger.net/web-security",
        "why": "The gold-standard free course on web app exploitation.",
        "cost": "Free",
        "time_estimate": "60+ hrs",
        "role_ids": ["pentester", "appsec_eng"],
        "domain_ids": ["offensive", "appsec"],
    },
    {
        "title": "OWASP Top 10 (2021)",
        "kind": "reference",
        "url": "https://owasp.org/Top10/",
        "why": "AppSec interviews assume fluency in this list.",
        "cost": "Free",
        "time_estimate": "ongoing",
        "role_ids": ["appsec_eng", "pentester"],
        "domain_ids": ["appsec", "offensive"],
    },
    {
        "title": "AWS Skill Builder — Security Learning Plans",
        "kind": "course",
        "url": "https://skillbuilder.aws/category/security",
        "why": "Free AWS-native security training, mapped to the Security Specialty.",
        "cost": "Free",
        "time_estimate": "40–60 hrs",
        "role_ids": ["cloudsec_eng", "junior_sec_eng"],
        "domain_ids": ["cloud", "engineering"],
    },
    {
        "title": "NIST Cybersecurity Framework 2.0",
        "kind": "reference",
        "url": "https://www.nist.gov/cyberframework",
        "why": "Foundational framework for any GRC role; used widely by enterprises.",
        "cost": "Free",
        "time_estimate": "10–20 hrs",
        "role_ids": ["grc_analyst", "compliance_mgr"],
        "domain_ids": ["grc"],
    },
    {
        "title": "Hack The Box — Starting Point",
        "kind": "lab",
        "url": "https://www.hackthebox.com/",
        "why": "Onramp to offensive practice before paid pentest tracks.",
        "cost": "Free tier",
        "time_estimate": "self-paced",
        "role_ids": ["pentester", "red_teamer"],
        "domain_ids": ["offensive"],
    },
    {
        "title": "TCM Security — Practical Network Penetration Tester (PNPT)",
        "kind": "certification",
        "url": "https://certifications.tcm-sec.com/pnpt/",
        "why": "Modern, lab-based pentest cert with real-world report deliverable.",
        "cost": "$399",
        "time_estimate": "12+ weeks",
        "role_ids": ["pentester"],
        "domain_ids": ["offensive"],
    },
    {
        "title": "Microsoft SC-900: Security, Compliance, and Identity Fundamentals",
        "kind": "certification",
        "url": "https://learn.microsoft.com/credentials/certifications/security-compliance-and-identity-fundamentals/",
        "why": "Cheap, broad cert covering the IAM and compliance vocabulary in Microsoft shops.",
        "cost": "$99",
        "time_estimate": "3–5 weeks",
        "role_ids": ["iam_eng", "grc_analyst"],
        "domain_ids": ["iam", "grc"],
    },
    {
        "title": "Cyber Defenders — Blue Team CTFs",
        "kind": "lab",
        "url": "https://cyberdefenders.org/",
        "why": "DFIR-flavored challenges that round out detection skills.",
        "cost": "Free + paid",
        "time_estimate": "self-paced",
        "role_ids": ["soc_t2", "ir", "forensics"],
        "domain_ids": ["soc", "dfir"],
    },
    {
        "title": "Sigma — Generic Detection Format",
        "kind": "reference",
        "url": "https://github.com/SigmaHQ/sigma",
        "why": "Detection-engineer interviews probe Sigma fluency hard.",
        "cost": "Free (open source)",
        "time_estimate": "ongoing",
        "role_ids": ["detection_eng", "soc_t2"],
        "domain_ids": ["soc"],
    },
    {
        "title": "Trail of Bits — Building Secure Contracts (book chapters online)",
        "kind": "book",
        "url": "https://secure-contracts.com/",
        "why": "Solid foundation in adversarial software thinking.",
        "cost": "Free",
        "time_estimate": "10–20 hrs",
        "role_ids": ["appsec_eng"],
        "domain_ids": ["appsec"],
    },
    {
        "title": "r/cybersecurity — Mentorship Mondays",
        "kind": "community",
        "url": "https://www.reddit.com/r/cybersecurity/",
        "why": "Weekly thread for newcomers to ask questions; recruiters lurk.",
        "cost": "Free",
        "time_estimate": "ongoing",
        "role_ids": [r for r in []],  # general
        "domain_ids": [],
    },
]


def resources_for(*, role_id: str | None = None, domain_id: str | None = None) -> list[Resource]:
    """Filter curated resources by role and/or domain.

    Falls back to the broader domain when no role-specific match exists.
    """
    out: list[Resource] = []
    for r in CURATED_RESOURCES:
        role_match = role_id is None or role_id in r["role_ids"] or not r["role_ids"]
        domain_match = domain_id is None or domain_id in r["domain_ids"] or not r["domain_ids"]
        if role_match and domain_match:
            out.append(r)
    return out
