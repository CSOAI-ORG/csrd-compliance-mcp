<div align="center">

# Csrd Compliance MCP

**MCP server for csrd compliance mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-csrd-compliance-mcp)](https://pypi.org/project/meok-csrd-compliance-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Csrd Compliance MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `classify_entity` | Classify when the entity must first report under CSRD. Returns first reporting F |
| `list_esrs_standards` | List all 12 ESRS topical standards + 2 cross-cutting. |
| `double_materiality_assessment` | Run a heuristic double materiality assessment. Double materiality = (a) impact o |
| `ghg_emissions_readiness` | Check ESRS E1 (Climate) Scope 1/2/3 emissions readiness. scopes_tracked: comma-s |
| `ixbrl_taxonomy_check` | Check readiness for mandatory iXBRL digital tagging of sustainability statements |
| `enforcement_status` | Current CSRD enforcement phase-in schedule + Member State transposition status. |
| `sign_csrd_attestation` | Generate a cryptographically signed CSRD / ESRS readiness attestation (Pro/Enter |

## Installation

```bash
pip install meok-csrd-compliance-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "csrd-compliance-mcp": {
      "command": "python",
      "args": ["-m", "meok_csrd_compliance_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 7 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
