# 🟦 Azure / Microsoft Foundry Setup for DENDRITE

> Everything below is done **in the web portal** (https://ai.azure.com and https://portal.azure.com). No Docker, no local container builds. The IQ layers (Foundry IQ, Fabric IQ, Work IQ) live inside Microsoft Foundry / Fabric — your code only **calls** them.

---

## 0. Prereqs

| Item | How |
|---|---|
| Azure subscription | <https://azure.microsoft.com/free> or **Azure for Students** ($100 free credit) |
| Microsoft Foundry access | sign in at <https://ai.azure.com> with your Azure account |
| Microsoft Fabric free trial | <https://app.fabric.microsoft.com> → start trial (60 days) |
| Region | Use **East US 2** or **Sweden Central** (best model availability) |

---

## 1. Resource Group + Storage + Search (5 min)

1. Portal → **Resource groups** → **Create** → `dendrite-rg`, region East US 2.
2. In `dendrite-rg` → **Create** → **Storage account** → `dendritekb<yourinitials>` → Standard LRS → review + create.
3. Inside the storage account → **Containers** → **+ Container** → name `dendrite-kb` → upload every file from `knowledge/` (the synthetic markdown).
4. In `dendrite-rg` → **Create** → **Azure AI Search** → name `dendrite-search` → **Free F0** tier → create.
5. After provisioning, open the search service → **Identity** → enable **System-assigned managed identity** (required for agentic retrieval).

---

## 2. Microsoft Foundry Project (5 min)

1. Go to <https://ai.azure.com> → ensure **New Foundry** toggle is ON.
2. **+ Create project** → name `dendrite` → choose your hub / region.
3. Project endpoint URL appears on the **Overview** page — copy it. Format:
   ```
   https://<your-foundry-resource>.services.ai.azure.com/api/projects/dendrite
   ```
   This is what testers paste into the **BYOK modal** in the frontend.

---

## 3. Deploy the 4 MIRL models (10 min)

Inside the Foundry project → **Models + endpoints** → **+ Deploy model**. Deploy these four:

| Model | Tier | Quota tip |
|---|---|---|
| `Phi-4-mini-instruct` | 🔵 1 — Instant | Microsoft serverless, near-free |
| `gpt-4o-mini` | 🟡 2 — CoT | Standard, very cheap |
| `gpt-4.1-mini` | 🟠 3 — Interleaved | Standard |
| `o4-mini` | 🔴 4 — Deep reasoning | Standard, used sparingly |

For each one give it the **deployment name shown in the table above** (keeps `mirl.py` simple).

> 💡 If `o4-mini` is not yet GA in your region, swap to `o3-mini` — DENDRITE auto-falls-back via env var `MIRL_TIER4_MODEL`.

---

## 4. Foundry IQ — Knowledge Base (15 min)

1. Foundry project → left nav → **Build** → **Knowledge** tab → **+ New knowledge base** → name `dendrite-foundry-iq`.
2. Pick the search service `dendrite-search` from step 1.
3. **+ Add knowledge source** → **Azure Blob Storage** → select `dendrite-kb` container.
4. Chunking: **512 tokens, 64 token overlap**, semantic enabled.
5. Run the indexer once. After ~2 min you should see all 6 documents indexed.
6. Go to **Agents** tab → **+ New agent** → name `dendrite-kb-agent` → connect to `dendrite-foundry-iq` → instructions:
   ```
   You retrieve cited content from the DENDRITE knowledge base.
   Every fact you return MUST include [Source: <doc>, §<section>].
   If no relevant content is found, say "No grounded information found" and stop.
   ```
7. Copy the **agent ID** — paste it into the BYOK modal field “Foundry KB Agent ID” (optional, only if you want pure-Foundry retrieval; DENDRITE also works via raw Azure AI Search).

---

## 5. Fabric IQ — Ontology (20 min)

1. Open <https://app.fabric.microsoft.com> → **+ Create** → **Lakehouse** → `dendrite_lakehouse`.
2. Upload the 3 JSON files from `data/synthetic/` (Get data → Upload files).
3. Convert each to a Delta table (right-click → **Load to tables**).
4. Left nav → **IQ** → **Ontology (preview)** → **+ New ontology** → `dendrite_ontology`.
5. Define these entities (the UI lets you click-create):

   | Entity | Key columns |
   |---|---|
   | Learner | learner_id, role |
   | Certification | id, recommended_hours |
   | SkillArea | name |
   | StudyOutcome | learner_id, certification, exam_outcome |
   | WorkSignal | employee_id, meeting_hours_per_week, focus_hours_per_week |

   Relationships:
   * Learner — takes → Certification
   * Certification — covers → SkillArea
   * Learner — produced → StudyOutcome
   * Learner — has → WorkSignal

6. Publish the ontology. Copy the **Fabric workspace ID** + **ontology ID**.
7. Paste those into the BYOK modal as **Fabric Workspace** + **Fabric Ontology ID**. The Fabric IQ service wrapper (`backend/services/fabric_iq.py`) calls the public Fabric REST API with the user's Entra token.

---

## 6. Work IQ

Work IQ is currently preview-restricted to certain M365 tenants. For demo correctness, DENDRITE ships a **synthetic Work IQ simulator** (`backend/services/work_iq_sim.py`) that uses the exact synthetic JSON shape from the challenge brief. It is **clearly labelled as a simulator everywhere in the UI and code**. When you graduate to a tenant with real Work IQ, swap the URL in `WORKIQ_URL` env var — no other code changes.

---

## 7. Microsoft Learn MCP

Public endpoint, no auth, free:

```
https://learn.microsoft.com/api/mcp
```

Wired up in `backend/services/mcp_learn.py`. No setup needed.

---

## 8. Hosted Agent (optional — for the deployment story)

When you want to host the final solution:

1. Push the `backend/` folder to **GitHub**.
2. Portal → **App Services** → **+ Create** → **Web App** → **Python 3.11** → Free F1 plan.
3. **Deployment Center** → connect GitHub repo → branch `main` → startup command:
   ```
   gunicorn -k uvicorn.workers.UvicornWorker backend.main:app --bind=0.0.0.0:8000
   ```
4. App Service → **Identity** → enable system-assigned managed identity → grant it `Cognitive Services User` on your Foundry project.
5. Frontend (Vite build) → push `frontend/dist/` to **Azure Static Web Apps Free**.

That gives you a published learner+manager experience with zero containers.

---

## 9. Cost alerts (1 min)

Portal → **Cost Management** → **Budgets** → create budget `dendrite-budget` = **$15** → alerts at 50% / 80% / 100%.

You will not exceed $14. MIRL keeps 80% of calls on Phi-4 + gpt-4o-mini.
