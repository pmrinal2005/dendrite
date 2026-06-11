import json
from pathlib import Path

from fastapi import APIRouter

from ..agents import meta_learning
from ..core import config
from ..core.logging import LOG_DIR
from ..models.schemas import HealthResponse

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/healthz", response_model=HealthResponse)
async def healthz() -> HealthResponse:
    return HealthResponse(
        ok=True,
        version="1.0.0",
        mirl_models={
            "tier1_instant": config.TIER1_MODEL,
            "tier2_cot": config.TIER2_MODEL,
            "tier3_interleaved": config.TIER3_MODEL,
            "tier4_deep": config.TIER4_MODEL,
        },
    )


@router.get("/reflect")
async def reflect() -> dict:
    out = meta_learning.reflect()
    return {
        "agent": out.agent,
        "confidence": out.confidence,
        "content": out.content,
        **out.extra,
    }


def _read_jsonl(name: str, limit: int) -> list[dict]:
    p: Path = LOG_DIR / f"{name}.jsonl"
    if not p.exists():
        return []
    rows: list[dict] = []
    try:
        with p.open() as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    except OSError:
        return []
    return rows[-limit:]


@router.get("/audit/recent")
async def audit_recent(limit: int = 50) -> list[dict]:
    return _read_jsonl("guardrail_audit", limit)


@router.get("/trace/recent")
async def trace_recent(limit: int = 100) -> list[dict]:
    return _read_jsonl("agent_trace", limit)
