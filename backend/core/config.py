"""
BYOK config. The frontend sends the user's Foundry endpoint + key via headers
on every request. We never persist them server-side.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from fastapi import Header, HTTPException


# ---------- model deployment names (must match what you deploy in Foundry) ----------
TIER1_MODEL = os.getenv("MIRL_TIER1_MODEL", "Phi-4-mini-instruct")
TIER2_MODEL = os.getenv("MIRL_TIER2_MODEL", "gpt-4o-mini")
TIER3_MODEL = os.getenv("MIRL_TIER3_MODEL", "gpt-4.1-mini")
TIER4_MODEL = os.getenv("MIRL_TIER4_MODEL", "o4-mini")

LEARN_MCP_URL = "https://learn.microsoft.com/api/mcp"

CONFIDENCE_GATE = float(os.getenv("CONFIDENCE_GATE", "0.72"))


@dataclass(frozen=True)
class UserContext:
    """Per-request BYOK context. Never logged, never persisted."""
    foundry_endpoint: str
    foundry_key: str
    foundry_kb_agent_id: Optional[str] = None
    fabric_workspace_id: Optional[str] = None
    fabric_ontology_id: Optional[str] = None


async def get_user_context(
    x_foundry_endpoint: Optional[str] = Header(default=None),
    x_foundry_key: Optional[str] = Header(default=None),
    x_foundry_kb_agent_id: Optional[str] = Header(default=None),
    x_fabric_workspace_id: Optional[str] = Header(default=None),
    x_fabric_ontology_id: Optional[str] = Header(default=None),
) -> UserContext:
    if not x_foundry_endpoint or not x_foundry_key:
        raise HTTPException(
            status_code=401,
            detail="Missing BYOK headers. Configure your Foundry endpoint + key in the UI.",
        )
    return UserContext(
        foundry_endpoint=x_foundry_endpoint.rstrip("/"),
        foundry_key=x_foundry_key,
        foundry_kb_agent_id=x_foundry_kb_agent_id,
        fabric_workspace_id=x_fabric_workspace_id,
        fabric_ontology_id=x_fabric_ontology_id,
    )
