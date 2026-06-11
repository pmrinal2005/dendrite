"""
Microsoft Learn MCP — public, free, no auth.

We use streamable HTTP. For DENDRITE we call the `microsoft_docs_search` tool
to fetch live, citation-bearing references that complement Foundry IQ.
"""
from __future__ import annotations

import httpx
import uuid
from typing import Any

from ..core.config import LEARN_MCP_URL


async def search_learn(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    """Best-effort: returns [{title, url, snippet}, ...] or [] on failure."""
    body = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "tools/call",
        "params": {
            "name": "microsoft_docs_search",
            "arguments": {"query": query},
        },
    }
    headers = {"Content-Type": "application/json",
               "Accept": "application/json, text/event-stream"}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.post(LEARN_MCP_URL, headers=headers, json=body)
            r.raise_for_status()
            data = r.json()
        content = (data.get("result") or {}).get("content") or []
        results: list[dict[str, Any]] = []
        for item in content[:top_k]:
            if item.get("type") == "text":
                text = item.get("text", "")
                # Each text item typically contains a short citation block
                results.append({"title": "Microsoft Learn",
                                "url": "https://learn.microsoft.com",
                                "snippet": text[:400]})
        return results
    except Exception:    # noqa: BLE001
        return []
