"""
Fabric IQ wrapper.

Fabric IQ Ontology lives in Microsoft Fabric. We expose a *minimal* helper
that returns the ontology entities/relationships if a workspace+ontology ID
was supplied. If not, we return a clearly-labelled placeholder so agents
gracefully degrade.

This module never hardcodes business data. The IQ layer is the source of truth.
"""
from __future__ import annotations

import httpx
from typing import Any

from ..core.config import UserContext


FABRIC_REST = "https://api.fabric.microsoft.com/v1"


async def get_ontology_snapshot(ctx: UserContext) -> dict[str, Any]:
    if not (ctx.fabric_workspace_id and ctx.fabric_ontology_id):
        return {
            "available": False,
            "note": "Fabric IQ workspace/ontology not configured — provide IDs in BYOK.",
            "entities": [],
            "relationships": [],
        }

    url = (f"{FABRIC_REST}/workspaces/{ctx.fabric_workspace_id}"
           f"/ontologies/{ctx.fabric_ontology_id}")
    headers = {"Authorization": f"Bearer {ctx.foundry_key}"}
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(url, headers=headers)
            if r.status_code != 200:
                return {"available": False, "note": f"Fabric IQ {r.status_code}",
                        "entities": [], "relationships": []}
            data = r.json()
            return {
                "available": True,
                "entities": data.get("entities", []),
                "relationships": data.get("relationships", []),
            }
    except Exception as e:    # noqa: BLE001
        return {"available": False, "note": str(e),
                "entities": [], "relationships": []}
