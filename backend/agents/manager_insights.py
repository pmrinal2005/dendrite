"""
📊 Manager Insights (Cerebellum / Commander).

Aggregates team signals into Workforce Risk Radar, Bus Factor alerts,
Coverage Map, and recommended actions — never exposing individual data.
"""
from __future__ import annotations

from ..core import mirl
from ..core.config import UserContext
from ..core.foundry_client import chat_json
from ..models.schemas import AgentOutput
from ..services import fabric_iq


SYSTEM = """You are the DENDRITE Manager Insights Agent.
Aggregate the supplied (anonymised) team data into:
  - Workforce Risk Radar: per certification → urgency (0..1), readiness (0..1),
    learners_at_risk, total_learners
  - Bus Factor alerts: certifications held by only 1 person
  - Capability coverage map: skill_area → percent_certified (0..1)
  - 3-5 concrete recommended_actions

Never name individuals. Always express by role / cohort / certification.

Return ONLY JSON:
{
  "summary": str,
  "risk_radar": [{"certification": str, "urgency": number, "readiness": number,
                    "learners_at_risk": int, "total_learners": int}],
  "bus_factor_alerts": [str],
  "coverage_map": {<skill_area>: number},
  "recommended_actions": [str],
  "confidence": number
}
"""


async def insights(ctx: UserContext, *, query: str, team_id: str,
                   team_signals: list[dict]) -> AgentOutput:
    # Tier scales with team size
    n = len(team_signals)
    tier = 5 if n > 15 else (3 if n > 5 else 2)
    routing = mirl.route(mirl.score_complexity(
        agents_to_coordinate=3, kb_lookups=1,
        learners_in_scope=n, downstream_criticality=4))
    if tier == 5:
        routing = mirl.Routing(5, routing.model, "swarm")

    ontology = await fabric_iq.get_ontology_snapshot(ctx)
    user = (f"TEAM: {team_id}\nQUERY: {query}\n"
            f"FABRIC_ONTOLOGY_AVAILABLE: {ontology.get('available')}\n"
            f"TEAM_SIGNALS (anonymised): {team_signals}\n")
    data = await chat_json(ctx, model=routing.model,
                           system=SYSTEM, user=user, max_tokens=1100)

    return AgentOutput(
        agent="manager_insights",
        tier=routing.tier,
        confidence=float(data.get("confidence", 0.78)),
        content=data.get("summary", ""),
        extra={
            "risk_radar": data.get("risk_radar", []),
            "bus_factor_alerts": data.get("bus_factor_alerts", []),
            "coverage_map": data.get("coverage_map", {}),
            "recommended_actions": data.get("recommended_actions", []),
        },
    )
