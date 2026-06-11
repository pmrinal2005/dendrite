from fastapi import APIRouter, Depends

from ..agents import assessment as a, guardrail
from ..core.config import UserContext, get_user_context
from ..models.schemas import (AssessmentRequest, AssessmentResponse,
                              ScoringRequest, ScoringResponse,
                              WeaknessFingerprint)

router = APIRouter(prefix="/assessment", tags=["assessment"])


@router.post("/generate", response_model=AssessmentResponse)
async def generate(req: AssessmentRequest,
                   ctx: UserContext = Depends(get_user_context)) -> AssessmentResponse:
    out, questions = await a.generate_questions(
        ctx, certification=req.certification,
        skill_areas=req.skill_areas, num_questions=req.num_questions)
    _, guard = guardrail.scan_output(
        out.content, [c.model_dump() for c in out.citations],
        agent="assessment_generator", requires_citations=True)
    return AssessmentResponse(questions=questions, trace=[out], guardrail=guard)


@router.post("/score", response_model=ScoringResponse)
async def score(req: ScoringRequest,
                ctx: UserContext = Depends(get_user_context)) -> ScoringResponse:
    out = await a.score(ctx, certification=req.certification,
                        answers=req.answers, questions=req.questions)
    _, guard = guardrail.scan_output(out.content, None,
                                     agent="assessment_scorer")
    return ScoringResponse(
        readiness_pct=out.extra.get("readiness_pct", 0.0),
        knowledge_temperature=out.extra.get("knowledge_temperature", "warm"),
        fingerprint=[WeaknessFingerprint(**fp)
                     for fp in out.extra.get("fingerprint", [])],
        next_action=out.content,
        socratic_followups=out.extra.get("socratic_followups", []),
        trace=[out],
        guardrail=guard,
    )
