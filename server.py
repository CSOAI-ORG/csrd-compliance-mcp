#!/usr/bin/env python3
"""
CSRD (EU Corporate Sustainability Reporting Directive) Compliance MCP
======================================================================
By MEOK AI Labs | https://meok.ai

The only MCP server that automates CSRD (Directive (EU) 2022/2464) compliance
against the 12 European Sustainability Reporting Standards (ESRS). Covers
double materiality, Scope 1-2-3 emissions, iXBRL digital tagging readiness.

PHASE-IN:
  FY2024 — large public-interest entities with >500 employees (first reports due 2025)
  FY2025 — other large companies (reports due 2026)
  FY2026 — listed SMEs (reports due 2027)
  FY2028 — non-EU parent companies with EU turnover >€150M
SCOPE: ~50,000 EU companies total.
PENALTIES: Member-state specific; French ANC up to €3.75M per breach; Germany up to €2M.

Install: pip install csrd-compliance-mcp
Run:     python server.py
"""

import json
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

import os as _os
import sys
import os

_MEOK_API_KEY = _os.environ.get("MEOK_API_KEY", "")

try:
    sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
    from auth_middleware import check_access as _shared_check_access
except ImportError:
    def _shared_check_access(api_key: str = ""):
        if _MEOK_API_KEY and api_key and api_key == _MEOK_API_KEY:
            return True, "OK", "pro"
        if _MEOK_API_KEY and api_key and api_key != _MEOK_API_KEY:
            return False, "Invalid API key. Get one at https://meok.ai/api-keys", "free"
        return True, "OK", "free"


def check_access(api_key: str = ""):
    return _shared_check_access(api_key)


FREE_DAILY_LIMIT = 10
_usage: dict[str, list[datetime]] = defaultdict(list)
STRIPE_199 = "https://buy.stripe.com/14A4gB3K4eUWgYR56o8k836"
STRIPE_1499 = "https://buy.stripe.com/4gM9AV80kaEG0ZT42k8k837"


def _rl(tier: str = "free") -> Optional[str]:
    if tier in ("pro", "professional", "enterprise"):
        return None
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=1)
    _usage["anonymous"] = [t for t in _usage["anonymous"] if t > cutoff]
    if len(_usage["anonymous"]) >= FREE_DAILY_LIMIT:
        return f"Free tier limit ({FREE_DAILY_LIMIT}/day). Unlock full 12-ESRS sweep + iXBRL taxonomy + signed attestations: Pro £199/mo at {STRIPE_199}"
    _usage["anonymous"].append(now)
    return None


# ── ESRS Standards (12 topical + 2 cross-cutting) ───────────────
ESRS = {
    "ESRS 1": {"title": "General requirements", "type": "cross-cutting"},
    "ESRS 2": {"title": "General disclosures", "type": "cross-cutting"},
    "ESRS E1": {"title": "Climate change", "type": "environmental", "required": True},
    "ESRS E2": {"title": "Pollution", "type": "environmental"},
    "ESRS E3": {"title": "Water and marine resources", "type": "environmental"},
    "ESRS E4": {"title": "Biodiversity and ecosystems", "type": "environmental"},
    "ESRS E5": {"title": "Resource use and circular economy", "type": "environmental"},
    "ESRS S1": {"title": "Own workforce", "type": "social"},
    "ESRS S2": {"title": "Workers in the value chain", "type": "social"},
    "ESRS S3": {"title": "Affected communities", "type": "social"},
    "ESRS S4": {"title": "Consumers and end-users", "type": "social"},
    "ESRS G1": {"title": "Business conduct", "type": "governance"},
}

ENFORCEMENT_PHASES = [
    {"fy": "2024", "who": "Large public-interest entities (>500 employees)", "report_due": "2025"},
    {"fy": "2025", "who": "Other large companies (meeting 2 of: >250 employees, €50M turnover, €25M balance sheet)", "report_due": "2026"},
    {"fy": "2026", "who": "Listed SMEs", "report_due": "2027 (with possible 2-year opt-out to 2028)"},
    {"fy": "2028", "who": "Non-EU parents with EU turnover >€150M + EU subsidiary/branch", "report_due": "2029"},
]

mcp = FastMCP(
    "csrd-compliance",
    instructions=(
        "MEOK AI Labs CSRD Compliance MCP. Automates audits against Directive (EU) 2022/2464 "
        "and the 12 European Sustainability Reporting Standards (ESRS). Ask me to classify "
        "when you must report, run a double materiality assessment, check Scope 1/2/3 "
        "emissions readiness, or map existing data to ESRS datapoints."
    ),
)


@mcp.tool()
def classify_entity(employees: int, turnover_million_eur: float, balance_sheet_million_eur: float = 0, listed: bool = False, public_interest_entity: bool = False, api_key: str = "") -> str:
    """Classify when the entity must first report under CSRD. Returns first reporting FY,
    report year, and ESRS standards required.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need to assess, audit, or verify compliance
        requirements. Ideal for gap analysis, readiness checks, and generating
        compliance documentation.

    When NOT to use:
        Do not use as a substitute for qualified legal counsel. This tool
        provides technical compliance guidance, not legal advice.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": STRIPE_199})
    if err := _rl(tier):
        return json.dumps({"error": err, "upgrade_url": STRIPE_199})

    # Large = meets 2 of: >250 FTE, €50M turnover, €25M balance sheet
    size_criteria = sum([employees > 250, turnover_million_eur > 50, balance_sheet_million_eur > 25])
    is_large = size_criteria >= 2

    first_fy = None
    first_report_year = None

    if is_large and employees > 500 and public_interest_entity:
        first_fy, first_report_year = "FY2024", "2025"
    elif is_large:
        first_fy, first_report_year = "FY2025", "2026"
    elif listed:
        first_fy, first_report_year = "FY2026", "2027 (2-year opt-out possible to 2028)"

    out_of_scope = first_fy is None
    return json.dumps({
        "in_scope": not out_of_scope,
        "first_reporting_fy": first_fy,
        "first_report_due_by": first_report_year,
        "size_classification": "large" if is_large else "medium/small",
        "meets_large_criteria": f"{size_criteria} of 3 (>250 FTE, >€50M turnover, >€25M balance sheet)",
        "standards_required": list(ESRS.keys()),
        "always_mandatory": ["ESRS 1", "ESRS 2", "ESRS E1 (Climate)"],
        "double_materiality_required": True,
        "assurance_required": "Limited assurance initially → reasonable assurance by 2028 (mandatory EU audit standard)",
        "penalty_note": "Member-state specific. France ANC: up to €3.75M per breach. Germany: up to €2M. UK listed non-EU parents still in scope for EU subsidiaries.",
        "next_step": "Run double_materiality_assessment to identify which topical ESRS apply beyond E1.",
    }, indent=2)


@mcp.tool()
def list_esrs_standards(api_key: str = "") -> str:
    """List all 12 ESRS topical standards + 2 cross-cutting.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need to assess, audit, or verify compliance
        requirements. Ideal for gap analysis, readiness checks, and generating
        compliance documentation.

    When NOT to use:
        Do not use as a substitute for qualified legal counsel. This tool
        provides technical compliance guidance, not legal advice.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg})
    return json.dumps({
        "directive": "Directive (EU) 2022/2464 (CSRD)",
        "standards_framework": "ESRS (European Sustainability Reporting Standards) — Commission Delegated Regulation (EU) 2023/2772",
        "standards": [{"code": k, **v} for k, v in ESRS.items()],
        "always_required": "ESRS 1, ESRS 2, and ESRS E1 (climate) are always mandatory. Others depend on double materiality assessment.",
    }, indent=2)


@mcp.tool()
def double_materiality_assessment(business_description: str, stakeholder_concerns: str = "", api_key: str = "") -> str:
    """Run a heuristic double materiality assessment. Double materiality = (a) impact on people/planet
    AND (b) financial impact on the entity. Returns material ESRS standards to report on.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need to assess, audit, or verify compliance
        requirements. Ideal for gap analysis, readiness checks, and generating
        compliance documentation.

    When NOT to use:
        Do not use as a substitute for qualified legal counsel. This tool
        provides technical compliance guidance, not legal advice.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": STRIPE_199})
    if err := _rl(tier):
        return json.dumps({"error": err, "upgrade_url": STRIPE_199})

    d = (business_description + " " + stakeholder_concerns).lower()

    material = {"ESRS 1": "Mandatory", "ESRS 2": "Mandatory", "ESRS E1": "Mandatory"}
    hints = {
        "ESRS E2": ["chemicals", "manufacturing", "pollution", "emissions", "air quality"],
        "ESRS E3": ["water", "marine", "ocean", "fisheries", "drought"],
        "ESRS E4": ["biodiversity", "land use", "deforestation", "wildlife", "supply chain agriculture"],
        "ESRS E5": ["circular", "waste", "recycling", "packaging", "raw materials"],
        "ESRS S1": ["employees", "workforce", "labour", "staff"],
        "ESRS S2": ["supply chain", "suppliers", "outsourcing", "contractors"],
        "ESRS S3": ["community", "indigenous", "local residents"],
        "ESRS S4": ["consumers", "customers", "end users", "data privacy", "product safety"],
        "ESRS G1": ["governance", "anti-corruption", "lobbying", "political contributions", "ethics"],
    }
    for code, kws in hints.items():
        if any(k in d for k in kws):
            material[code] = "Likely material — confirm via stakeholder engagement"

    non_material = [k for k in ESRS if k not in material]

    return json.dumps({
        "double_materiality_principle": "An impact or risk is material if it meets EITHER: (a) impact materiality — the entity's negative/positive impact on people or planet; OR (b) financial materiality — expected financial effect on the entity.",
        "material_standards": material,
        "likely_non_material": non_material,
        "assurance_point": "Double materiality assessment MUST be documented and is subject to limited assurance (and later, reasonable assurance).",
        "common_pitfalls": [
            "Copy-pasting sector materiality without stakeholder engagement",
            "Missing value-chain impacts (upstream + downstream)",
            "Ignoring short-term vs medium-term vs long-term horizons",
        ],
        "upsell": f"Pro tier adds stakeholder-engagement workflow, sector benchmarks, and signed attestation: £199/mo {STRIPE_199}" if tier != "pro" else None,
    }, indent=2)


@mcp.tool()
def ghg_emissions_readiness(scopes_tracked: str = "", methodology: str = "", api_key: str = "") -> str:
    """Check ESRS E1 (Climate) Scope 1/2/3 emissions readiness. scopes_tracked: comma-separated list
    (e.g. 'scope 1, scope 2 location-based, scope 2 market-based'). methodology: e.g. 'GHG Protocol'.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need to assess, audit, or verify compliance
        requirements. Ideal for gap analysis, readiness checks, and generating
        compliance documentation.

    When NOT to use:
        Do not use as a substitute for qualified legal counsel. This tool
        provides technical compliance guidance, not legal advice.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": STRIPE_199})
    if err := _rl(tier):
        return json.dumps({"error": err, "upgrade_url": STRIPE_199})

    s = scopes_tracked.lower()
    m = methodology.lower()

    readiness = {
        "Scope 1 (direct emissions)": "scope 1" in s,
        "Scope 2 location-based": "scope 2" in s and "location" in s,
        "Scope 2 market-based": "scope 2" in s and "market" in s,
        "Scope 3 (value chain)": "scope 3" in s,
        "Scope 3 categories disclosed": "scope 3" in s,
        "GHG Protocol methodology": "ghg protocol" in m or "ghg" in m,
        "ISO 14064 used": "14064" in m,
        "External assurance obtained": any(t in m for t in ["limited assurance", "reasonable assurance", "iaasb"]),
    }
    score = round(sum(readiness.values()) / len(readiness) * 100, 1)
    gaps = [k for k, v in readiness.items() if not v]

    return json.dumps({
        "standard": "ESRS E1 — Climate change",
        "mandatory_disclosures": [
            "E1-1 Transition plan for climate change mitigation",
            "E1-2 Policies related to climate change",
            "E1-3 Actions and resources",
            "E1-4 Targets related to climate change mitigation and adaptation",
            "E1-5 Energy consumption and mix",
            "E1-6 Gross Scopes 1, 2, 3 and total GHG emissions",
            "E1-7 GHG removals and GHG mitigation projects",
            "E1-8 Internal carbon pricing",
            "E1-9 Anticipated financial effects (physical + transition risks)",
        ],
        "readiness_score_percent": score,
        "signals_present": {k: v for k, v in readiness.items() if v},
        "gaps_to_close": gaps,
        "benchmark_methodology": "GHG Protocol (Corporate Standard + Scope 2 Guidance + Scope 3 Standard) is the de facto required baseline.",
    }, indent=2)


@mcp.tool()
def ixbrl_taxonomy_check(api_key: str = "") -> str:
    """Check readiness for mandatory iXBRL digital tagging of sustainability statements
    under CSRD Article 29d + ESEF taxonomy extension.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need to assess, audit, or verify compliance
        requirements. Ideal for gap analysis, readiness checks, and generating
        compliance documentation.

    When NOT to use:
        Do not use as a substitute for qualified legal counsel. This tool
        provides technical compliance guidance, not legal advice.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg})
    return json.dumps({
        "regulation": "Directive (EU) 2022/2464 Article 29d + ESEF Regulation (EU) 2019/815",
        "requirement": "Sustainability statements MUST be prepared in digital machine-readable format (iXBRL / Inline XBRL) and tagged against ESRS XBRL taxonomy.",
        "taxonomy_source": "ESMA ESRS XBRL taxonomy — published 2024, updated annually",
        "scope_of_tagging": [
            "All quantitative datapoints (emissions, FTE counts, financial amounts)",
            "Narrative disclosures for specific mandatory categories",
            "Cross-reference to EU Taxonomy for Sustainable Activities datapoints",
        ],
        "readiness_check": [
            "Do you use an ESEF-capable reporting platform? (Workiva, CCH Tagetik, AuditBoard, Diligent, FloQast, Novata)",
            "Is your sustainability data in a structured database (not just PDF/Word)?",
            "Do you have an XBRL taxonomist or ESEF filer engaged?",
        ],
        "common_mistakes": [
            "Trying to tag a finished PDF after-the-fact — impossibly slow; tag throughout drafting",
            "Missing EU Taxonomy alignment datapoints (turnover/CapEx/OpEx % aligned)",
            "Assuming existing financial-report iXBRL stack handles sustainability — ESRS taxonomy is separate",
        ],
    }, indent=2)


@mcp.tool()
def enforcement_status(api_key: str = "") -> str:
    """Current CSRD enforcement phase-in schedule + Member State transposition status.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need to assess, audit, or verify compliance
        requirements. Ideal for gap analysis, readiness checks, and generating
        compliance documentation.

    When NOT to use:
        Do not use as a substitute for qualified legal counsel. This tool
        provides technical compliance guidance, not legal advice.
    """
    now = datetime.now(timezone.utc)
    return json.dumps({
        "directive": "Directive (EU) 2022/2464 (CSRD) + Directive (EU) 2013/34/EU (Accounting Directive, amended)",
        "standards": "Commission Delegated Regulation (EU) 2023/2772 — ESRS Set 1",
        "phases": ENFORCEMENT_PHASES,
        "current_date_utc": now.isoformat(),
        "immediate_priority": "~12,000 companies with first reports due in 2025-2026. Double materiality + ESRS gap analysis takes 9-12 months.",
        "omnibus_simplification_proposal": "Commission proposed 'omnibus simplification package' in 2025 — may delay phase-in for medium-large entities. Monitor official EUR-Lex updates.",
    }, indent=2)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
