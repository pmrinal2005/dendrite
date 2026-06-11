# 🧠 DENDRITE
### Cognitive Nervous System for Enterprise Learning · Built on Microsoft Foundry

> A 10-Agent multi-agent reasoning system powered by Microsoft Agent Framework, Foundry IQ, Fabric IQ, and Work IQ — engineered for the **Reasoning Agents** track of the Microsoft Agents League.

⚠️ **All data in this repository is entirely synthetic.** No real employees, no PII, no customer data. Identifiers like `EMP-001`, `L-1001`, `TEAM-A` are fictional and only used as seed examples from the official challenge brief.

---

## 🏆 Why DENDRITE wins

| Pillar | What we built |
|---|---|
| **Architecture** | 10-Agent Cognitive Nervous System (Prefrontal Cortex, Hippocampus, Amygdala, Cerebellum, Immune System, Default Mode Network…) |
| **Reasoning** | 5-Tier Model Intelligence Routing Layer (MIRL) using cheapest-effective models per task |
| **Grounding** | Foundry IQ (knowledge) + Fabric IQ (ontology) + Work IQ (work context) + Microsoft Learn MCP |
| **Safety** | Silent Guardrail Agent: 6-dimension checks + full audit trail |
| **Quality** | Critic/Verifier invoked only when confidence < 0.72 (~15% of outputs) |
| **Self-Improvement** | Meta-Learning Memory Agent — first enterprise LMS with a Default-Mode-Network agent |
| **Frontend** | Jaw-dropping SaaS UI: React + Vite + Tailwind + Framer Motion + Recharts + neural-network animated background |
| **BYOK** | Every tester enters their own Foundry endpoint + key in the frontend — no shared credits |
| **Cost** | Total estimated spend **$8–$14** for the entire build |

---

## 💰 Ultra-Low-Cost Model Strategy ($8–$14 total)

DENDRITE uses **MIRL (Model Intelligence Routing Layer)** to dispatch tasks to the cheapest model that can still reason well. We benchmarked the Foundry Model Catalog and selected:

| Tier | Model | Where to deploy | Per-1M tokens (in / out) | Used for |
|---|---|---|---|---|
| 🔵 1 — Instant | **Phi-4-mini-instruct** | Foundry → Models → Microsoft (free / serverless) | ~$0.00 | Routing, intent parsing, status, FAQ, simple nudges |
| 🟡 2 — CoT | **gpt-4o-mini** | Azure OpenAI in Foundry | ~$0.15 / $0.60 | Plan generation, gap detection, Engagement |
| 🟠 3 — Interleaved | **gpt-4.1-mini** | Azure OpenAI in Foundry | ~$0.40 / $1.60 | Path curation, assessment question gen |
| 🔴 4 — Deep Reasoning | **o4-mini** (reasoning) | Azure OpenAI in Foundry | ~$1.10 / $4.40 | Critic, complex assessment scoring |
| ⚫ 5 — Swarm | mix of Tier 1 + Tier 3 merge | Foundry workflow | optimized | Team-scale Manager Insights |

**80% of requests land on Tier 1–2** → realistic spend ≈ **$11**. Stays well inside Azure Student Pack.

---

## 🧬 The 10-Agent Cognitive Nervous System

| Brain Region | Agent | File | MIRL Tier |
|---|---|---|---|
| Prefrontal Cortex | 🧠 Meta-Orchestrator | `backend/agents/orchestrator.py` | 1–2 |
| Hippocampus | 📚 Learning Path Curator | `backend/agents/path_curator.py` | 3 |
| Cerebellum | 📅 Study Plan Generator | `backend/agents/plan_generator.py` | 2–3 |
| Motor + Amygdala | 🔔 Engagement Agent | `backend/agents/engagement.py` | 1–2 |
| Hippocampus + Cerebellum | 🎯 Assessment Agent | `backend/agents/assessment.py` | 3–4 |
| Cerebellum | 📊 Manager Insights | `backend/agents/manager_insights.py` | 3–5 |
| Immune System | 🛡️ Guardrail Agent | `backend/agents/guardrail.py` | 2 |
| Basal Ganglia | 🔁 Critic / Verifier | `backend/agents/critic.py` | 4 |
| Reticular Formation | 🕐 Skill Decay Detector | `backend/agents/skill_decay.py` | 1 (mostly math) |
| Default Mode Network ⭐ | 🧠💭 Meta-Learning Memory | `backend/agents/meta_learning.py` | 2 (async) |

---

## 🗺️ Phase-by-Phase Build Plan (compressed for a low-end laptop, no Docker)

### Phase 0 — Prep (~2 h)
1. Activate Azure Student account ($100 credit).
2. Create Microsoft Foundry project at <https://ai.azure.com>.
3. Install Python 3.10+, Node 18+, Git, VS Code.
4. Clone this repo, create `.venv`, `pip install -r backend/requirements.txt`.
5. `cd frontend && npm install`.

### Phase 1 — Foundry setup (~3 h, done in the web portal — see `docs/AZURE_SETUP.md`)
1. Create resource group `dendrite-rg`.
2. Create **Azure AI Search (Free F0)** and **Azure Blob Storage**.
3. Upload `knowledge/*.md` to a blob container `dendrite-kb`.
4. In Foundry portal → **Build → Knowledge** → create knowledge base `dendrite-foundry-iq` → connect Blob.
5. In Foundry → **Models** → deploy: `gpt-4o-mini`, `gpt-4.1-mini`, `o4-mini`, `Phi-4-mini-instruct`.
6. In **Microsoft Fabric** (free trial) → create Lakehouse → enable **Fabric IQ → Ontology (preview)** → seed with the entities described in `docs/AZURE_SETUP.md`.
7. Work IQ stays as a **synthetic simulator** in code (preview restrictions) — clearly labelled.

### Phase 2 — Backend (~6 h)
1. `backend/core/config.py` — BYOK config from request headers.
2. `backend/core/mirl.py` — complexity scoring + tier routing.
3. Implement the 10 agents under `backend/agents/`.
4. `backend/main.py` — FastAPI app with `/chat`, `/assessment`, `/manager`, `/healthz`.
5. Run with `uvicorn backend.main:app --reload --port 8000`.

### Phase 3 — Frontend (~6 h)
1. React + Vite + TypeScript + Tailwind + shadcn-style components.
2. Landing page with animated neural-network canvas (`NeuralBackground.tsx`).
3. **BYOK Modal** — user enters Foundry endpoint + key, stored in `localStorage` only.
4. Three workspaces: **Learner**, **Manager**, **System Health** (MIRL analytics).
5. Recharts dashboards: Readiness Gauge, Weakness Radar, Risk Radar, Decay Curve, MIRL distribution.

### Phase 4 — Eval & polish (~3 h)
1. Run `backend/evals/scenarios.py` against all agents.
2. Verify Guardrail catches fake citations and PII attempts.
3. Record 5-min demo.

### Phase 5 — Hosted deployment (no Docker, no local laptop pain)
Use **Foundry Agent Service** “Connected Agents” + the FastAPI app deployed to **Azure App Service Free F1** (or run locally and tunnel via `ngrok` for the demo). Container path is documented but not required for judging.

---

## 🛠️ Tech Stack

**Backend** — FastAPI · Microsoft Agent Framework (`agent-framework` Python SDK) · Azure AI Foundry SDK · Azure Identity · httpx · pydantic v2 · Supabase Python client (optional persistence).

**Frontend** — React 18 · Vite 5 · TypeScript · TailwindCSS · Framer Motion · Recharts · Lucide Icons · Zustand · React Router. No backend secrets; **BYOK** via headers.

**Data layer** — Foundry IQ (Azure AI Search F0) · Fabric IQ Ontology · Work IQ simulator · Supabase (free tier) for session + audit logs (optional).

**No Docker.** Everything runs on Python + Node only.

---

## 🚀 Run locally

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
# open http://localhost:5173
```

Open the UI, click **Connect Foundry**, paste your endpoint + key, and explore. Nothing leaves your browser except direct calls to your own Foundry resource.

---

## 🔐 Responsible AI & Security

* Silent Guardrail Agent runs on **every** output: citation check, PII scan, hallucination probe, bias, prompt-injection, scope.
* Full audit log streamed to `backend/logs/guardrail_audit.jsonl`.
* BYOK: no server-side secrets. Keys live in the browser only.
* `.env` and `*.key` blocked via `.gitignore`.
* AI disclosure on session start.

---

## 📂 Project Structure

```
dendrite/
├── README.md
├── .gitignore
├── docs/
│   ├── AZURE_SETUP.md          # step-by-step Foundry / Fabric / Search setup
│   ├── ARCHITECTURE.md
│   └── SUPABASE_SCHEMA.sql
├── knowledge/                  # synthetic markdown for Foundry IQ
│   ├── engineering-certification-guide.md
│   ├── team-learning-report.md
│   └── workload-insights-report.md
├── data/synthetic/
│   ├── learners.json
│   ├── work-signals.json
│   └── certifications.json
├── backend/
│   ├── requirements.txt
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── mirl.py
│   │   ├── foundry_client.py
│   │   └── logging.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   ├── path_curator.py
│   │   ├── plan_generator.py
│   │   ├── engagement.py
│   │   ├── assessment.py
│   │   ├── manager_insights.py
│   │   ├── guardrail.py
│   │   ├── critic.py
│   │   ├── skill_decay.py
│   │   └── meta_learning.py
│   ├── services/
│   │   ├── foundry_iq.py        # thin wrapper — IQ lives in Foundry
│   │   ├── fabric_iq.py         # thin wrapper — Fabric IQ lives in Fabric
│   │   ├── work_iq_sim.py       # synthetic Work IQ simulator (preview gap)
│   │   └── mcp_learn.py         # Microsoft Learn MCP client
│   ├── routers/
│   │   ├── chat.py
│   │   ├── assessment.py
│   │   ├── manager.py
│   │   └── system.py
│   └── models/schemas.py
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── tsconfig.json
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── lib/{api.ts, store.ts, utils.ts}
        ├── hooks/useChat.ts
        ├── styles/index.css
        ├── components/
        │   ├── NeuralBackground.tsx
        │   ├── BYOKModal.tsx
        │   ├── Sidebar.tsx
        │   ├── ChatPanel.tsx
        │   ├── AgentTrace.tsx
        │   ├── ReadinessGauge.tsx
        │   ├── WeaknessRadar.tsx
        │   ├── RiskRadar.tsx
        │   └── MIRLDistribution.tsx
        └── pages/
            ├── Landing.tsx
            ├── Learner.tsx
            ├── Manager.tsx
            └── SystemHealth.tsx
```

---

## 📚 Evaluation Criteria Mapping

| Criterion | Weight | Where DENDRITE delivers |
|---|---|---|
| Accuracy & Relevance | 25% | Foundry IQ citation-grounded retrieval + Critic loop |
| Reasoning & Multi-step | 25% | 10 agents · MIRL · Planner-Executor-Critic · Swarm Tier 5 |
| Creativity & Originality | 15% | Cognitive Nervous System metaphor · Meta-Learning DMN agent · MIRL |
| UX & Presentation | 15% | Animated neural background · live agent trace · BYOK modal · Recharts dashboards |
| Reliability & Safety | 20% | Guardrail 6-D checks · audit log · synthetic data only · no secrets · BYOK |

---

## 🙏 Credits

Built for the **Microsoft Agents League — Reasoning Agents (Battle #2)** track.
Inspired by reasoning science from DeepSeek R1, Kimi K2.6, Qwen3, Claude Sonnet 4.6, and cognitive research (Ebbinghaus, Bjork, SM-2, IRT/CAT).
