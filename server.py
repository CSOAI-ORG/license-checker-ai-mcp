"""
License Checker AI MCP Server
Open source license identification and compatibility tools powered by MEOK AI Labs.
"""

import time
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("license-checker-ai-mcp")

_call_counts: dict[str, list[float]] = defaultdict(list)
FREE_TIER_LIMIT = 50
WINDOW = 86400

LICENSES = {
    "MIT": {"spdx": "MIT", "type": "permissive", "copyleft": False, "patent_grant": False,
            "summary": "Very permissive. Allows commercial use, modification, distribution. Requires attribution."},
    "Apache-2.0": {"spdx": "Apache-2.0", "type": "permissive", "copyleft": False, "patent_grant": True,
                   "summary": "Permissive with explicit patent grant. Requires attribution and change notice."},
    "GPL-3.0": {"spdx": "GPL-3.0-only", "type": "copyleft", "copyleft": True, "patent_grant": True,
                "summary": "Strong copyleft. Derivatives must use GPL-3.0. Includes patent grant."},
    "GPL-2.0": {"spdx": "GPL-2.0-only", "type": "copyleft", "copyleft": True, "patent_grant": False,
                "summary": "Strong copyleft. Derivatives must use GPL-2.0."},
    "LGPL-3.0": {"spdx": "LGPL-3.0-only", "type": "weak-copyleft", "copyleft": True, "patent_grant": True,
                 "summary": "Weak copyleft. Can link without copyleft obligations for the linking code."},
    "BSD-2-Clause": {"spdx": "BSD-2-Clause", "type": "permissive", "copyleft": False, "patent_grant": False,
                     "summary": "Very permissive. Similar to MIT but simpler terms."},
    "BSD-3-Clause": {"spdx": "BSD-3-Clause", "type": "permissive", "copyleft": False, "patent_grant": False,
                     "summary": "Permissive. Like BSD-2 but adds non-endorsement clause."},
    "MPL-2.0": {"spdx": "MPL-2.0", "type": "weak-copyleft", "copyleft": True, "patent_grant": True,
                "summary": "File-level copyleft. Modified files must stay MPL, but can combine with other code."},
    "ISC": {"spdx": "ISC", "type": "permissive", "copyleft": False, "patent_grant": False,
            "summary": "Functionally equivalent to MIT. Very permissive."},
    "Unlicense": {"spdx": "Unlicense", "type": "public-domain", "copyleft": False, "patent_grant": False,
                  "summary": "Public domain dedication. No restrictions whatsoever."},
    "CC0-1.0": {"spdx": "CC0-1.0", "type": "public-domain", "copyleft": False, "patent_grant": False,
                "summary": "Creative Commons public domain. No rights reserved."},
    "AGPL-3.0": {"spdx": "AGPL-3.0-only", "type": "copyleft", "copyleft": True, "patent_grant": True,
                 "summary": "Network copyleft. Server use triggers distribution obligations."},
}

COMPAT_MATRIX = {
    ("MIT", "MIT"): True, ("MIT", "Apache-2.0"): True, ("MIT", "GPL-3.0"): True,
    ("MIT", "GPL-2.0"): True, ("MIT", "BSD-2-Clause"): True, ("MIT", "BSD-3-Clause"): True,
    ("Apache-2.0", "Apache-2.0"): True, ("Apache-2.0", "GPL-3.0"): True,
    ("Apache-2.0", "GPL-2.0"): False, ("GPL-3.0", "GPL-3.0"): True,
    ("GPL-2.0", "GPL-3.0"): False, ("GPL-3.0", "MIT"): False, ("GPL-3.0", "Apache-2.0"): False,
    ("AGPL-3.0", "GPL-3.0"): True, ("AGPL-3.0", "MIT"): False,
}

FINGERPRINTS = {
    "Permission is hereby granted, free of charge": "MIT",
    "Apache License, Version 2.0": "Apache-2.0",
    "GNU GENERAL PUBLIC LICENSE": "GPL",
    "GNU LESSER GENERAL PUBLIC LICENSE": "LGPL-3.0",
    "Mozilla Public License Version 2.0": "MPL-2.0",
    "Redistribution and use in source and binary forms": "BSD",
    "This is free and unencumbered software": "Unlicense",
    "ISC License": "ISC",
    "CC0 1.0 Universal": "CC0-1.0",
}


def _check_rate_limit(tool_name: str) -> None:
    now = time.time()
    _call_counts[tool_name] = [t for t in _call_counts[tool_name] if now - t < WINDOW]
    if len(_call_counts[tool_name]) >= FREE_TIER_LIMIT:
        raise ValueError(f"Rate limit exceeded for {tool_name}. Free tier: {FREE_TIER_LIMIT}/day. Upgrade at https://meok.ai/pricing")
    _call_counts[tool_name].append(now)


@mcp.tool()
def identify_license(text: str) -> dict:
    """Identify the license type from license text content.

    Args:
        text: License text content to identify
    """
    _check_rate_limit("identify_license")
    matches = []
    for fingerprint, license_id in FINGERPRINTS.items():
        if fingerprint.lower() in text.lower():
            matches.append(license_id)
    if not matches:
        return {"identified": None, "confidence": 0.0, "message": "Could not identify license"}
    best = matches[0]
    if best == "GPL":
        best = "GPL-3.0" if "Version 3" in text else "GPL-2.0"
    elif best == "BSD":
        best = "BSD-3-Clause" if "endorsement" in text.lower() or "Neither the name" in text else "BSD-2-Clause"
    info = LICENSES.get(best, {})
    return {"identified": best, "confidence": min(len(matches) * 0.5, 1.0), "info": info}


@mcp.tool()
def check_compatibility(license_a: str, license_b: str) -> dict:
    """Check if two licenses are compatible for combining code.

    Args:
        license_a: First license identifier (e.g., 'MIT', 'GPL-3.0')
        license_b: Second license identifier
    """
    _check_rate_limit("check_compatibility")
    a, b = license_a.upper().replace(" ", "-"), license_b.upper().replace(" ", "-")
    a_info = LICENSES.get(a, {})
    b_info = LICENSES.get(b, {})
    if not a_info or not b_info:
        return {"compatible": None, "error": f"Unknown license(s). Known: {', '.join(LICENSES.keys())}"}
    compat = COMPAT_MATRIX.get((a, b), COMPAT_MATRIX.get((b, a)))
    if compat is None:
        if not a_info.get("copyleft") and not b_info.get("copyleft"):
            compat = True
        elif a_info.get("copyleft") and b_info.get("copyleft"):
            compat = a == b
        else:
            compat = True
    notes = []
    if a_info.get("copyleft"):
        notes.append(f"{a} is copyleft - combined work must use {a}")
    if b_info.get("copyleft"):
        notes.append(f"{b} is copyleft - combined work must use {b}")
    return {"license_a": a, "license_b": b, "compatible": compat, "notes": notes,
            "a_type": a_info.get("type"), "b_type": b_info.get("type")}


@mcp.tool()
def generate_license(license_type: str, author: str, year: int = 0) -> dict:
    """Generate license text for common open source licenses.

    Args:
        license_type: License type (MIT, Apache-2.0, BSD-2-Clause, ISC, Unlicense)
        author: Copyright holder name
        year: Copyright year (default: current year)
    """
    _check_rate_limit("generate_license")
    from datetime import date as _date
    if not year:
        year = _date.today().year
    templates = {
        "MIT": f"""MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""",
        "ISC": f"""ISC License

Copyright (c) {year} {author}

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.""",
        "Unlicense": """This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute
this software, either in source code form or as a compiled binary, for any
purpose, commercial or non-commercial, and by any means.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. IN NO EVENT
SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY.""",
    }
    lt = license_type.upper().replace(" ", "-")
    if lt not in templates:
        return {"error": f"Template available for: {', '.join(templates.keys())}"}
    return {"license_text": templates[lt], "license_type": lt, "author": author, "year": year}


@mcp.tool()
def explain_terms(license_type: str) -> dict:
    """Explain the key terms and obligations of a license in plain language.

    Args:
        license_type: License identifier (e.g., 'MIT', 'GPL-3.0', 'Apache-2.0')
    """
    _check_rate_limit("explain_terms")
    lt = license_type.upper().replace(" ", "-")
    info = LICENSES.get(lt)
    if not info:
        return {"error": f"Unknown license. Known: {', '.join(LICENSES.keys())}"}
    permissions = ["Commercial use", "Modification", "Distribution", "Private use"]
    conditions = ["License and copyright notice"]
    limitations = ["No liability", "No warranty"]
    if info["copyleft"]:
        conditions.append("Disclose source")
        conditions.append("Same license for derivatives")
    if info["patent_grant"]:
        permissions.append("Patent use")
    if lt == "AGPL-3.0":
        conditions.append("Network use is distribution")
    return {"license": lt, "type": info["type"], "summary": info["summary"],
            "permissions": permissions, "conditions": conditions, "limitations": limitations,
            "copyleft": info["copyleft"], "patent_grant": info["patent_grant"]}


if __name__ == "__main__":
    mcp.run()
