"""
🧠💭 Meta-Learning Memory (Default Mode Network) — UNIQUE TO DENDRITE.

Reads the system's own audit + trace logs, mines outcome patterns, and emits
hints used by Path Curator and Plan Generator on subsequent runs.

Stateless from the API's perspective — we don't persist user data; we only
read append-only JSONL logs on the server.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from ..core import config, mirl
from ..models.schemas import AgentOutput


LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def _read_jsonl(name: str) -> list[dict]:
    p = LOG_DIR / f"{name}.jsonl"
    if not p.exists():
        return []
    out: list[dict] = []
    with p.open() as f:
        for line in f:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def reflect() -> AgentOutput:
    routing = mirl.Routing(2, config.TIER2_MODEL, "cot")  # batch, very cheap
    audits = _read_jsonl("guardrail_audit")
    traces = _read_jsonl("agent_trace")

    violation_counts = Counter()
    for a in audits:
        for v in a.get("violations", []):
            violation_counts[v] += 1

    tier_counts = Counter()
    low_conf_agents = Counter()
    for t in traces:
        tier_counts[t.get("tier")] += 1
        if t.get("confidence", 1.0) < 0.72:
            low_conf_agents[t.get("agent")] += 1

    hints: list[str] = []
    if violation_counts.get("missing_citation", 0) > 3:
        hints.append("Path Curator should require ≥2 sources before answering.")
    if low_conf_agents.get("plan_generator", 0) > 2:
        hints.append("Plan Generator: prefer the Balanced variant when Work IQ load >18h.")
    if tier_counts.get(4, 0) > tier_counts.get(2, 0):
        hints.append("MIRL drift: too many Tier-4 escalations — tighten confidence gate.")

    return AgentOutput(
        agent="meta_learning",
        tier=routing.tier,
        confidence=0.85,
        content=f"Reflected over {len(audits)} audits and {len(traces)} traces.",
        extra={
            "violation_counts": dict(violation_counts),
            "tier_counts": dict(tier_counts),
            "low_confidence_agents": dict(low_conf_agents),
            "hints": hints,
        },
    )
