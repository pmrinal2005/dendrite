import { useStore } from './store';

export type ChatRequest = {
  message: string;
  learner_id?: string;
  role?: string;
  target_certification?: string;
  weeks_available?: number;
  persona?: 'learner' | 'manager';
};

export type AgentOutput = {
  agent: string;
  tier: number;
  confidence: number;
  content: string;
  citations: { doc: string; section?: string; excerpt?: string }[];
  extra: Record<string, any>;
};

export type ChatResponse = {
  reply: string;
  state: string;
  trace: AgentOutput[];
  guardrail: { intervened: boolean; violations: string[]; note?: string };
  citations: { doc: string; section?: string; excerpt?: string }[];
};

function headers() {
  const b = useStore.getState().byok;
  if (!b) throw new Error('BYOK not configured');
  const h: Record<string, string> = {
    'Content-Type': 'application/json',
    'x-foundry-endpoint': b.endpoint,
    'x-foundry-key': b.key
  };
  if (b.kbAgentId) h['x-foundry-kb-agent-id'] = b.kbAgentId;
  if (b.fabricWorkspaceId) h['x-fabric-workspace-id'] = b.fabricWorkspaceId;
  if (b.fabricOntologyId) h['x-fabric-ontology-id'] = b.fabricOntologyId;
  return h;
}

function base() {
  return useStore.getState().byok?.backendBase || 'http://localhost:8000';
}

export async function chat(req: ChatRequest): Promise<ChatResponse> {
  const r = await fetch(`${base()}/chat`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(req)
  });
  if (!r.ok) throw new Error(`Chat failed: ${r.status} ${await r.text()}`);
  return r.json();
}

export async function generateAssessment(payload: {
  certification: string;
  skill_areas: string[];
  num_questions: number;
}) {
  const r = await fetch(`${base()}/assessment/generate`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(payload)
  });
  if (!r.ok) throw new Error(`Assessment failed: ${r.status}`);
  return r.json();
}

export async function scoreAssessment(payload: any) {
  const r = await fetch(`${base()}/assessment/score`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(payload)
  });
  if (!r.ok) throw new Error(`Score failed: ${r.status}`);
  return r.json();
}

export async function managerInsights(payload: { query: string; team_id?: string }) {
  const r = await fetch(`${base()}/manager`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(payload)
  });
  if (!r.ok) throw new Error(`Manager failed: ${r.status}`);
  return r.json();
}

export async function systemReflect() {
  const r = await fetch(`${base()}/system/reflect`);
  return r.json();
}

export async function recentTrace() {
  const r = await fetch(`${base()}/system/trace/recent`);
  return r.json();
}

export async function recentAudit() {
  const r = await fetch(`${base()}/system/audit/recent`);
  return r.json();
}

export async function healthz() {
  const r = await fetch(`${base()}/system/healthz`);
  return r.json();
}
