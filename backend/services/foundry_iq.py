"""
Foundry IQ wrapper.

Foundry IQ itself lives in Microsoft Foundry — we do NOT re-implement retrieval.
We call the user's Foundry KB Agent (created in the Foundry portal, see
docs/AZURE_SETUP.md §4) via the Azure AI Agents REST surface.

If the user did not provide a KB agent ID, we fall back to a clearly-labelled
'no-grounding' response so the rest of the system keeps reasoning honestly.
"""
from __future__ import annotations

import httpx
from typing import Any

from ..core.config import UserContext


async def query_knowledge(ctx: UserContext, query: str) -> dict[str, Any]:
    """
    Returns { 'answer': str, 'citations': [{doc, section, excerpt}, ...] }.
    """
    if not ctx.foundry_kb_agent_id:
        return {
            "answer": "",
            "citations": [],
            "note": "Foundry IQ KB agent not configured — provide its ID in BYOK.",
        }

    url = f"{ctx.foundry_endpoint}/threads?api-version=2024-12-01-preview"
    headers = {
        "api-key": ctx.foundry_key,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=45.0) as client:
        # 1) create thread
        t = await client.post(url, headers=headers, json={})
        t.raise_for_status()
        thread_id = t.json()["id"]

        # 2) add message
        await client.post(
            f"{ctx.foundry_endpoint}/threads/{thread_id}/messages?api-version=2024-12-01-preview",
            headers=headers,
            json={"role": "user", "content": query},
        )
        # 3) run with KB agent
        r = await client.post(
            f"{ctx.foundry_endpoint}/threads/{thread_id}/runs?api-version=2024-12-01-preview",
            headers=headers,
            json={"assistant_id": ctx.foundry_kb_agent_id},
        )
        r.raise_for_status()
        run_id = r.json()["id"]

        # 4) poll
        for _ in range(30):
            s = await client.get(
                f"{ctx.foundry_endpoint}/threads/{thread_id}/runs/{run_id}?api-version=2024-12-01-preview",
                headers=headers,
            )
            status = s.json().get("status")
            if status in ("completed", "failed", "cancelled", "expired"):
                break
            import asyncio
            await asyncio.sleep(1.0)

        # 5) read last assistant message
        m = await client.get(
            f"{ctx.foundry_endpoint}/threads/{thread_id}/messages?api-version=2024-12-01-preview",
            headers=headers,
        )
        msgs = m.json().get("data", [])
        answer = ""
        citations: list[dict[str, Any]] = []
        for msg in msgs:
            if msg.get("role") == "assistant":
                for part in msg.get("content", []):
                    if part.get("type") == "text":
                        answer = part["text"]["value"]
                        for ann in part["text"].get("annotations", []):
                            if ann.get("type") == "file_citation":
                                citations.append({
                                    "doc": ann.get("text", "source"),
                                    "section": None,
                                    "excerpt": None,
                                })
                break

    return {"answer": answer, "citations": citations}
