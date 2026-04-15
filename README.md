# License Checker Ai

> By [MEOK AI Labs](https://meok.ai) — MEOK AI Labs MCP Server

License Checker AI MCP Server

## Installation

```bash
pip install license-checker-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install license-checker-ai-mcp
```

## Tools

### `identify_license`
Identify the license type from license text content.

**Parameters:**
- `text` (str)

### `check_compatibility`
Check if two licenses are compatible for combining code.

**Parameters:**
- `license_a` (str)
- `license_b` (str)

### `generate_license`
Generate license text for common open source licenses.

**Parameters:**
- `license_type` (str)
- `author` (str)
- `year` (int)

### `explain_terms`
Explain the key terms and obligations of a license in plain language.

**Parameters:**
- `license_type` (str)


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/license-checker-ai-mcp](https://github.com/CSOAI-ORG/license-checker-ai-mcp)
- **PyPI**: [pypi.org/project/license-checker-ai-mcp](https://pypi.org/project/license-checker-ai-mcp/)

## License

MIT — MEOK AI Labs
