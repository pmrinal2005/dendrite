"""
Thin async wrapper around the user's Foundry / Azure OpenAI deployment.

We use the OpenAI Python SDK pointed at the user's Foundry endpoint with
their key (BYOK). No keys are persisted server-side.
"""
from __future__ import annotations

import json
from typing import Any

import httpx
from openai import AsyncAzureOpenAI

from . import config
from .config import UserContext


def _client(ctx: UserContext) -> AsyncAzureOpenAI:
    # Foundry endpoint looks like:
    #   https://<resource>.services.ai.azure.com/api/projects/<project>
    # OpenAI SDK wants the resource root; strip the /api/projects/... suffix.
    base = ctx.foundry_endpoint
    if "/api/projects/" in base:
        base = base.split("/api/projects/")[0]
    return AsyncAzureOpenAI(
        api_key=ctx.foundry_key,
        api_version="2024-12-01-preview",
        azure_endpoint=base,
    )


async def chat(
    ctx: UserContext,
    *,
    model: str,
    system: str,
    user: str,
    temperature: float = 0.4,
    json_mode: bool = False,
    max_tokens: int = 900,
) -> str:
    client = _client(ctx)
    extra: dict[str, Any] = {}
    if json_mode:
        extra["response_format"] = {"type": "json_object"}
    # o-series reasoning models don't accept temperature
    is_reasoning = model.startswith("o")
    if is_reasoning:
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            max_completion_tokens=max_tokens,
            **extra,
        )
    else:
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            temperature=temperature,
            max_tokens=max_tokens,
            **extra,
        )
    return resp.choices[0].message.content or ""


async def chat_json(ctx: UserContext, *, model: str, system: str, user: str,
                    max_tokens: int = 900) -> dict:
    """Force JSON output and parse safely."""
    raw = await chat(ctx, model=model, system=system, user=user,
                     json_mode=True, max_tokens=max_tokens, temperature=0.2)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # last-resort: try to extract a JSON blob
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end != -1:
            return json.loads(raw[start:end + 1])
        raise
