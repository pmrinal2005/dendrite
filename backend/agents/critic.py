"""
🔁 Critic / Verifier (Basal Ganglia).

Invoked only when a sub-agent returns confidence < CONFIDENCE_GATE (0.72).
Uses Tier 4 (o4-mini) deep reasoning.
Returns: VALIDATED | REVISED | REJECTED.
"""
from __future__ import annotations

from typing import Any

from ..core import config, mirl
from ..core.foundry_client import chat_json
from ..core.config import UserContext
from ..models.schemas import AgentOutput


SYSTEM = """You are the DENDRITE Critic. Evaluate the provided agent output.
Apply counter-factual reasoning: "what could go wrong?".
Return ONLY JSON with keys:
  verdict: "validated" | "revised" | "rejected"
  reasoning: 1-3 sentences
  revised_output: string (if verdict == "revised", else "")
  new_confidence: number in [0,1]
"""


async def critique(ctx: UserContext, *, agent_name: str,
                   original: str, original_conf: float,
                   context_hint: str = "") -> AgentOutput:
    routing = mirl.Routing(4, config.TIER4_MODEL, "deep")
    user = (f"Agent under review: {agent_name}\n"
            f"Original confidence: {original_conf:.2f}\n"
            f"Context: {context_hint or 'n/a'}\n\n"
            f"--- Agent output ---\n{original}\n")
    try:
        data: dict[str, Any] = await chat_json(
            ctx, model=routing.model, system=SYSTEM, user=user, max_tokens=600
        )
    except Exception as e:    # noqa: BLE001
        return AgentOutput(agent="critic", tier=4, confidence=original_conf,
                           content=original,
                           extra={"verdict": "validated", "error": str(e)})

    verdict = data.get("verdict", "validated")
    revised = data.get("revised_output") or original
    new_conf = float(data.get("new_confidence", original_conf))
    return AgentOutput(
        agent="critic",
        tier=4,
        confidence=new_conf,
        content=revised if verdict == "revised" else original,
        extra={"verdict": verdict, "reasoning": data.get("reasoning", "")},
    )
