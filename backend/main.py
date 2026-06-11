"""
DENDRITE — FastAPI entrypoint.

Run:
    uvicorn backend.main:app --reload --port 8000
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import assessment, chat, manager, system

app = FastAPI(
    title="DENDRITE",
    version="1.0.0",
    description=(
        "Cognitive Nervous System for Enterprise Learning — "
        "10-agent reasoning system on Microsoft Foundry. "
        "All data is synthetic per challenge brief."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # BYOK only — no server secrets
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
        "ai_disclosure": ("You are interacting with an AI multi-agent system. "
                          "All data is synthetic."),
        "docs": "/docs",
    }
