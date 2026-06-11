import json
from pathlib import Path

from fastapi import APIRouter, Depends

from ..agents import manager_insights, guardrail
from ..core.config import UserContext, get_user_context
from ..models.schemas import (ManagerRequest, ManagerResponse, RiskCell)

router = APIRouter(prefix="/manager", tags=["manager"])

DATA = Path(__file__).resolve().parent.parent.parent / "data" / "synthetic"


def _team_signals() -> list[dict]:
    """Anonymised aggregate of the synthetic learner data from the challenge brief."""
    with (DATA / "learners.json").open() as f:
        learners = json.load(f)
    # strip learner_id; keep role/cert/score/hours/outcome
    return [{k: v for k, v in r.items() if k != "learner_id"} for r in learners]


@router.post("", response_model=ManagerResponse)
async def manager(req: ManagerRequest,
                  ctx: UserContext = Depends(get_user_context)) -> ManagerResponse:
    out = await manager_insights.insights(
        ctx, query=req.query, team_id=req.team_id or "TEAM-A",
        team_signals=_team_signals())
    _, guard = guardrail.scan_output(out.content, None,
                                     agent="manager_insights")
    return ManagerResponse(
        summary=out.content,
        risk_radar=[RiskCell(**r) for r in out.extra.get("risk_radar", [])],
        bus_factor_alerts=out.extra.get("bus_factor_alerts", []),
        coverage_map=out.extra.get("coverage_map", {}),
        recommended_actions=out.extra.get("recommended_actions", []),
        trace=[out],
        guardrail=guard,
    )
