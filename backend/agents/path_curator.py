"""
📚 Learning Path Curator (Hippocampus).

Grounded in Foundry IQ + Microsoft Learn MCP. Produces 3 alternative
learning paths with citations. Confidence reflects citation coverage.
"""
from __future__ import annotations

from typing import Any

from ..core import config, mirl
from ..core.config import UserContext
from ..core.foundry_client import chat_json
from ..models.schemas import AgentOutput, Citation
from ..services import foundry_iq, mcp_learn


SYSTEM = """You are the DENDRITE Learning Path Curator.
Given a role and target certification, produce THREE alternative learning paths.

Rules:
- Every recommendation must reference one of the supplied SOURCES by ID.
- If a fact is not in the SOURCES, do NOT invent it — flag a gap instead.
- Score each path on effort (1-5), risk (1-5), synergy (1-5), time_to_value_weeks.

Return ONLY JSON:
{
  "prerequisite_warning": string,
  "paths": [
     {"name": "Aggressive"|"Balanced"|"Conservative",
      "weeks": int,
      "modules": [{"title": str, "source_id": str}],
      "effort": int, "risk": int, "synergy": int,
      "readiness_confidence": number}
  ],
  "confidence": number
}
"""


async def curate(ctx: UserContext, *, role: str, certification: str,
                 weeks_available: int | None = None) -> AgentOutput:
    routing = mirl.route(mirl.score_complexity(
        agents_to_coordinate=2, kb_lookups=2,
        learners_in_scope=1, downstream_criticality=3))

    # ground: Foundry IQ + MS Learn MCP in parallel
    kb_query = (f"Learning path for a {role} preparing for {certification}. "
                "Include prerequisites, skill areas, recommended hours.")
    iq = await foundry_iq.query_knowledge(ctx, kb_query)
    learn = await mcp_learn.search_learn(f"{certification} {role} certification path")

    sources: list[dict[str, Any]] = []
    for i, c in enumerate(iq.get("citations", []) or []):
        sources.append({"id": f"IQ-{i+1}", "title": c.get("doc"),
                        "excerpt": iq.get("answer", "")[:600]})
    for j, l in enumerate(learn):
        sources.append({"id": f"MSL-{j+1}", "title": l["title"],
                        "url": l["url"], "excerpt": l["snippet"]})

    user_prompt = (
        f"Role: {role}\nCertification: {certification}\n"
        f"Weeks available: {weeks_available or 'flexible'}\n\n"
        f"SOURCES:\n" + "\n".join(
            f"- {s['id']}: {s.get('title','')} — {s.get('excerpt','')[:300]}"
            for s in sources
        ) + ("\n(no sources retrieved)" if not sources else "")
    )
    data = await chat_json(ctx, model=routing.model,
                           system=SYSTEM, user=user_prompt, max_tokens=900)

    citations = [Citation(doc=s.get("title", s["id"]),
                          section=s.get("id"),
                          excerpt=(s.get("excerpt") or "")[:240])
                 for s in sources]

    return AgentOutput(
        agent="path_curator",
        tier=routing.tier,
        confidence=float(data.get("confidence", 0.7 if citations else 0.55)),
        content=data.get("prerequisite_warning", "") or "Curated learning paths ready.",
        citations=citations,
        extra={"paths": data.get("paths", [])},
    )
