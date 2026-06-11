# DENDRITE — Architecture

```
                       ┌─────────────────────────────────────────────┐
   USER (browser)  →   │  React + Vite Frontend  (BYOK in headers)   │
                       └─────────────────┬───────────────────────────┘
                                         │   x-foundry-endpoint
                                         │   x-foundry-key
                                         ▼
                       ┌─────────────────────────────────────────────┐
                       │     FastAPI Backend  (uvicorn, no Docker)   │
                       │  /chat  /assessment  /manager  /system      │
                       └─────────────────┬───────────────────────────┘
                                         │
                          ┌──────────────┴──────────────┐
                          ▼                             ▼
                ┌─────────────────┐        ┌──────────────────────┐
                │ 🧠 Orchestrator │  ───▶  │   MIRL Router        │
                │  (Prefrontal)   │        │   complexity → tier  │
                └──────┬──────────┘        └────────┬─────────────┘
                       │                            │
        ┌──────────────┼─────────┬─────────┬────────┴────────┬──────────────┐
        ▼              ▼         ▼         ▼                 ▼              ▼
   📚 Curator   📅 PlanGen   🔔 Engage  🎯 Assess     📊 Manager       🕐 Decay
   (Hippo)     (Cereb.)     (Motor)    (Hippo+Cer)   (Cereb.)         (Retic.)
        │              │         │         │                 │              │
        └──────────────┴────┬────┴────┬────┴────────┬────────┴──────┬───────┘
                            ▼         ▼             ▼               ▼
                      🛡️ Guardrail (Immune)   🔁 Critic (Basal)  🧠💭 Meta-Learn (DMN)
                            │                       │               │
                            └───────────┬───────────┴───────────────┘
                                        ▼
              ┌───────────────────────────────────────────────────────────┐
              │   GROUND-TRUTH LAYERS  (all hosted in Microsoft Foundry)  │
              │   • Foundry IQ  (Azure AI Search F0)                      │
              │   • Fabric IQ   (Ontology in Microsoft Fabric)            │
              │   • Work IQ     (synthetic simulator until tenant-ready)  │
              │   • MS Learn MCP (https://learn.microsoft.com/api/mcp)    │
              └───────────────────────────────────────────────────────────┘
```

State machine inside the Orchestrator:

```
INTAKE → CURATION → PLANNING → ACTIVE_LEARNING → ASSESSMENT
                                          │
                                          ▼
                              pass? ─┬─yes─→ ADVANCE
                                     └─no──→ loop back to PLANNING (weak domains only)
```

Confidence gate: every sub-agent returns `{output, confidence ∈ [0,1]}`.
If `confidence < 0.72` → invoke Critic (Tier 4) → returns VALIDATED / REVISED / REJECTED.

Guardrail runs **after every agent** as middleware:
1. Citation verification
2. PII scan
3. Hallucination probe
4. Bias check
5. Prompt-injection detection
6. Out-of-scope detection
