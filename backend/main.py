"""
DENDRITE — FastAPI entrypoint.

Run locally:
    cd backend && uvicorn main:app --reload --port 8000
Or from repo root:
    uvicorn backend.main:app --reload --port 8000
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Make relative imports work in both `cd backend && uvicorn main:app`
# and `uvicorn backend.main:app` invocations.
_HERE = Path(__file__).resolve().parent
if str(_HERE.parent) not in sys.path:
    sys.path.insert(0, str(_HERE.parent))

try:
    from backend.routers import assessment, chat, manager, system
except ImportError:
    # Fallback when run from inside backend/
    from routers import assessment, chat, manager, system  # type: ignore

app = FastAPI(
    title="DENDRITE",
    version="1.0.0",
    description=(
        "Cognitive Nervous System for Enterprise Learning — "
        "10-agent reasoning system on Microsoft Azure AI Foundry. "
        "All data is synthetic per challenge brief."
    ),
)

_origins_env = os.getenv("CORS_ORIGINS", "*")
allow_origins = ["*"] if _origins_env.strip() == "*" else [
    o.strip() for o in _origins_env.split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

app.include_router(chat.router)
app.include_router(assessment.router)
app.include_router(manager.router)
app.include_router(system.router)


@app.get("/")
async def root() -> dict:
    return {
        "name": "DENDRITE",
        "tagline": "Cognitive Nervous System for Enterprise Learning",
        "ai_disclosure": (
            "You are interacting with an AI multi-agent system. "
            "All data is synthetic."
        ),
        "docs": "/docs",
        "health": "/healthz",
    }


@app.get("/healthz")
async def healthz_root() -> dict:
    # Render's health check hits /healthz at the root
    return {"ok": True, "service": "dendrite-backend"}
