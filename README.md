[![csrd-compliance-mcp MCP server](https://glama.ai/mcp/servers/CSOAI-ORG/csrd-compliance-mcp/badges/card.svg)](https://glama.ai/mcp/servers/CSOAI-ORG/csrd-compliance-mcp)

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/csrd-compliance-mcp)](https://pypi.org/project/csrd-compliance-mcp/)
[![Downloads](https://img.shields.io/pypi/dm/csrd-compliance-mcp)](https://pypi.org/project/csrd-compliance-mcp/)
[![GitHub stars](https://img.shields.io/github/stars/CSOAI-ORG/csrd-compliance-mcp)](https://github.com/CSOAI-ORG/csrd-compliance-mcp/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

# CSRD Compliance MCP

**EU Corporate Sustainability Reporting Directive (2022/2464) compliance automation. Entity classification, ESRS standards mapping, double materiality, GHG readiness, and iXBRL taxonomy checks.**

[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-224+_servers-purple)](https://meok.ai)

[Install](#install) · [Tools](#tools) · [Pricing](#pricing) · [Attestation API](#attestation-api)

</div>

---

## Why This Exists

The CSRD brings approximately 50,000 EU companies into mandatory sustainability reporting scope, replacing the Non-Financial Reporting Directive. Large undertakings must report from FY 2024, listed SMEs from FY 2026. Reports must follow the European Sustainability Reporting Standards (ESRS), pass limited assurance, and be filed in machine-readable iXBRL format.

Double materiality assessment alone typically takes 8-12 weeks with a Big 4 firm. This MCP classifies your entity scope, lists applicable ESRS standards, performs double materiality assessments, evaluates GHG emissions readiness across Scopes 1-3, validates iXBRL taxonomy compliance, and tracks enforcement status across member states.

## Install

```bash
pip install csrd-compliance-mcp
```

## Tools

| Tool | CSRD/ESRS Reference | What it does |
|------|---------------------|--------------|
| `classify_entity` | Directive Art. 2 | Determine CSRD scope based on size, listing, and PIE status |
| `list_esrs_standards` | ESRS 1-2, E1-E5, S1-S4, G1 | List all applicable ESRS standards for your entity |
| `double_materiality_assessment` | ESRS 1 Ch. 3 | Perform double materiality assessment (impact + financial) |
| `ghg_emissions_readiness` | ESRS E1 | Evaluate GHG emissions reporting readiness (Scope 1/2/3) |
| `ixbrl_taxonomy_check` | ESEF Regulation | Validate iXBRL taxonomy alignment for digital filing |
| `enforcement_status` | Per member state | Track transposition and enforcement deadlines by country |

## Example

```
Prompt: "Classify our company for CSRD scope. We have 800 employees,
EUR 45M turnover, EUR 22M balance sheet, not listed, not a PIE.
We operate in Germany and France."

Result: Entity classified as large undertaking (exceeds 2 of 3 size
criteria). In scope from FY 2025 reporting. Must apply full ESRS
cross-cutting and topical standards. Double materiality assessment
required. iXBRL digital filing mandatory. German BaFin enforcement
active, French AMF transposition confirmed.
```

## Pricing

| Tier | Price | What you get |
|------|-------|-------------|
| **Free** | £0 | 10 calls/day — entity classification + ESRS listing |
| **Pro** | £199/mo | Unlimited + HMAC-signed attestations + verify URLs |
| **Enterprise** | £1,499/mo | Multi-tenant + co-branded reports + webhooks |

[Subscribe to Pro](https://buy.stripe.com/14A4gB3K4eUWgYR56o8k836) · [Enterprise](https://buy.stripe.com/4gM9AV80kaEG0ZT42k8k837)

## Attestation API

Every Pro/Enterprise audit produces a cryptographically signed certificate:

```
POST https://meok-attestation-api.vercel.app/sign
GET  https://meok-attestation-api.vercel.app/verify/{cert_id}
```

Zero-dep verifier: `pip install meok-attestation-verify`

## Links

- Website: [meok.ai](https://meok.ai)
- All MCP servers: [meok.ai/labs/mcp/servers](https://meok.ai/labs/mcp/servers)
- Enterprise support: nicholas@csoai.org

## License

MIT
