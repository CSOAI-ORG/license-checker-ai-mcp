<div align="center">

# License Checker Ai MCP

**License Checker AI MCP Server**

[![PyPI](https://img.shields.io/pypi/v/meok-license-checker-ai-mcp)](https://pypi.org/project/meok-license-checker-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

License Checker AI MCP Server
Open source license identification and compatibility tools powered by MEOK AI Labs.

## Tools

| Tool | Description |
|------|-------------|
| `identify_license` | Identify the license type from license text content. |
| `check_compatibility` | Check if two licenses are compatible for combining code. |
| `generate_license` | Generate license text for common open source licenses. |
| `explain_terms` | Explain the key terms and obligations of a license in plain language. |

## Installation

```bash
pip install meok-license-checker-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "license-checker-ai": {
      "command": "python",
      "args": ["-m", "meok_license_checker_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
