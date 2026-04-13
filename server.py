"""
License Checker AI MCP Server
Software license identification and compatibility tools powered by MEOK AI Labs.
"""

import re
import time
from collections import defaultdict
from datetime import date
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("license-checker-ai-mcp")

_call_counts: dict[str, list[float]] = defaultdict(list)
FREE_TIER_LIMIT = 50
WINDOW = 86400

def _check_rate_limit(tool_name: str) -> None:
    now = time.time()
    _call_counts[tool_name] = [t for t in _call_counts[tool_name] if now - t < WINDOW]
    if len(_call_counts[tool_name]) >= FREE_TIER_LIMIT:
        raise ValueError(f"Rate limit exceeded for {tool_name}. Free tier: {FREE_TIER_LIMIT}/day. Upgrade at https://meok.ai/pricing")
    _call_counts[tool_name].append(now)

LICENSES = {
    "MIT": {"spdx": "MIT", "type": "permissive", "copyleft": False, "osi_approved": True,
            "permissions": ["commercial", "modify", "distribute", "private_use"],
            "conditions": ["include_copyright", "include_license"],
            "limitations": ["no_liability", "no_warranty"],
            "keywords": ["permission is hereby granted, free of charge", "mit license"]},
    "Apache-2.0": {"spdx": "Apache-2.0", "type": "permissive", "copyleft": False, "osi_approved": True,
            "permissions": ["commercial", "modify", "distribute", "patent_use", "private_use"],
            "conditions": ["include_copyright", "include_license", "state_changes", "include_notice"],
            "limitations": ["no_liability", "no_warranty", "no_trademark"],
            "keywords": ["apache license", "version 2.0"]},
    "GPL-3.0": {"spdx": "GPL-3.0-only", "type": "copyleft", "copyleft": True, "osi_approved": True,
            "permissions": ["commercial", "modify", "distribute", "patent_use", "private_use"],
            "conditions": ["disclose_source", "include_copyright", "include_license", "same_license", "state_changes"],
            "limitations": ["no_liability", "no_warranty"],
            "keywords": ["gnu general public license", "version 3"]},
    "BSD-3-Clause": {"spdx": "BSD-3-Clause", "type": "permissive", "copyleft": False, "osi_approved": True,
            "permissions": ["commercial", "modify", "distribute", "private_use"],
            "conditions": ["include_copyright", "include_license"],
            "limitations": ["no_liability", "no_warranty"],
            "keywords": ["redistribution and use in source and binary", "neither the name"]},
    "ISC": {"spdx": "ISC", "type": "permissive", "copyleft": False, "osi_approved": True,
            "permissions": ["commercial", "modify", "distribute", "private_use"],
            "conditions": ["include_copyright", "include_license"],
            "limitations": ["no_liability", "no_warranty"],
            "keywords": ["isc license", "permission to use, copy, modify"]},
    "AGPL-3.0": {"spdx": "AGPL-3.0-only", "type": "copyleft", "copyleft": True, "osi_approved": True,
            "permissions": ["commercial", "modify", "distribute", "patent_use", "private_use"],
            "conditions": ["disclose_source", "include_copyright", "network_use_is_distribution", "same_license"],
            "limitations": ["no_liability", "no_warranty"],
            "keywords": ["gnu affero general public license", "version 3"]},
    "LGPL-3.0": {"spdx": "LGPL-3.0-only", "type": "weak_copyleft", "copyleft": True, "osi_approved": True,
            "permissions": ["commercial", "modify", "distribute", "patent_use", "private_use"],
            "conditions": ["disclose_source", "include_copyright", "include_license", "same_license_library"],
            "limitations": ["no_liability", "no_warranty"],
            "keywords": ["gnu lesser general public license", "version 3"]},
    "Unlicense": {"spdx": "Unlicense", "type": "public_domain", "copyleft": False, "osi_approved": True,
            "permissions": ["commercial", "modify", "distribute", "private_use"],
            "conditions": [], "limitations": ["no_liability", "no_warranty"],
            "keywords": ["this is free and unencumbered software", "unlicense"]},
}

COMPAT = {
    ("MIT", "MIT"): True, ("MIT", "Apache-2.0"): True, ("MIT", "GPL-3.0"): True,
    ("Apache-2.0", "Apache-2.0"): True, ("Apache-2.0", "GPL-3.0"): True,
    ("GPL-3.0", "GPL-3.0"): True, ("GPL-3.0", "MIT"): False,
    ("GPL-3.0", "Apache-2.0"): False, ("AGPL-3.0", "GPL-3.0"): False,
    ("MIT", "AGPL-3.0"): True, ("BSD-3-Clause", "MIT"): True,
    ("BSD-3-Clause", "GPL-3.0"): True, ("ISC", "MIT"): True,
}


@mcp.tool()
def identify_license(text: str) -> dict:
    """Identify a software license from its text content.

    Args:
        text: License text content to identify
    """
    _check_rate_limit("identify_license")
    text_lower = text.lower()
    scores = {}
    for name, info in LICENSES.items():
        score = sum(3 for kw in info["keywords"] if kw in text_lower)
        if score > 0:
            scores[name] = score
    if not scores:
        return {"identified": None, "confidence": "none", "message": "Could not identify license"}
    best = max(scores, key=scores.get)
    confidence = "high" if scores[best] >= 6 else "medium" if scores[best] >= 3 else "low"
    info = LICENSES[best]
    return {"identified": best, "spdx": info["spdx"], "type": info["type"],
            "confidence": confidence, "copyleft": info["copyleft"],
            "osi_approved": info["osi_approved"], "other_matches": {k: v for k, v in scores.items() if k != best}}


@mcp.tool()
def check_compatibility(license_a: str, license_b: str) -> dict:
    """Check if two licenses are compatible for use together.

    Args:
        license_a: First license SPDX identifier (e.g., 'MIT')
        license_b: Second license SPDX identifier (e.g., 'GPL-3.0')
    """
    _check_rate_limit("check_compatibility")
    a = license_a.upper().replace("_", "-")
    b = license_b.upper().replace("_", "-")
    # Normalize
    for key in LICENSES:
        if a.upper() == key.upper():
            a = key
        if b.upper() == key.upper():
            b = key
    compatible = COMPAT.get((a, b), COMPAT.get((b, a)))
    info_a = LICENSES.get(a, {})
    info_b = LICENSES.get(b, {})
    notes = []
    if info_a.get("copyleft") and not info_b.get("copyleft"):
        notes.append(f"{a} is copyleft - derivative works must use {a}")
    if info_b.get("copyleft") and not info_a.get("copyleft"):
        notes.append(f"{b} is copyleft - derivative works must use {b}")
    return {"license_a": a, "license_b": b,
            "compatible": compatible if compatible is not None else "unknown",
            "notes": notes,
            "a_type": info_a.get("type", "unknown"), "b_type": info_b.get("type", "unknown")}


@mcp.tool()
def generate_license(license_type: str, holder: str = "", year: str = "") -> dict:
    """Generate a license text file for the given license type.

    Args:
        license_type: License identifier (MIT, Apache-2.0, BSD-3-Clause, ISC, Unlicense)
        holder: Copyright holder name
        year: Copyright year (default: current year)
    """
    _check_rate_limit("generate_license")
    if not year:
        year = str(date.today().year)
    templates = {
        "MIT": f"""MIT License

Copyright (c) {year} {holder}

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

Copyright (c) {year} {holder}

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

Anyone is free to copy, modify, publish, use, compile, sell, or distribute this
software, either in source code form or as a compiled binary, for any purpose,
commercial or non-commercial, and by any means.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.""",
    }
    lt = license_type.strip()
    template = templates.get(lt)
    if not template:
        return {"error": f"Template not available for {lt}. Available: {list(templates.keys())}"}
    return {"license_type": lt, "text": template, "holder": holder, "year": year}


@mcp.tool()
def explain_terms(license_type: str) -> dict:
    """Explain what a license allows, requires, and prohibits in plain English.

    Args:
        license_type: License identifier (e.g., 'MIT', 'GPL-3.0', 'Apache-2.0')
    """
    _check_rate_limit("explain_terms")
    info = LICENSES.get(license_type)
    if not info:
        return {"error": f"Unknown license: {license_type}. Known: {list(LICENSES.keys())}"}
    perm_text = {"commercial": "Use commercially", "modify": "Modify the source",
                 "distribute": "Distribute copies", "patent_use": "Use patents",
                 "private_use": "Use privately"}
    cond_text = {"include_copyright": "Must include copyright notice",
                 "include_license": "Must include license text", "state_changes": "Must state changes made",
                 "disclose_source": "Must disclose source code", "same_license": "Derivatives must use same license",
                 "same_license_library": "Library modifications must use same license",
                 "include_notice": "Must include NOTICE file", "network_use_is_distribution": "Network use counts as distribution"}
    limit_text = {"no_liability": "No liability accepted", "no_warranty": "No warranty provided",
                  "no_trademark": "No trademark rights granted"}
    return {"license": license_type, "spdx": info["spdx"], "type": info["type"],
            "copyleft": info["copyleft"], "osi_approved": info["osi_approved"],
            "permissions": [perm_text.get(p, p) for p in info["permissions"]],
            "conditions": [cond_text.get(c, c) for c in info["conditions"]],
            "limitations": [limit_text.get(l, l) for l in info["limitations"]],
            "summary": f"{license_type} is a {'copyleft' if info['copyleft'] else 'permissive'} license that "
                       f"{'requires derivative works to be open-sourced' if info['copyleft'] else 'allows use with minimal restrictions'}."}


if __name__ == "__main__":
    mcp.run()
