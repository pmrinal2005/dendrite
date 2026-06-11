import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Activity, RefreshCw } from 'lucide-react';
import { healthz, recentAudit, recentTrace, systemReflect } from '../lib/api';
import MIRLDistribution from '../components/MIRLDistribution';

export default function SystemHealthPage() {
  const [hz, setHz] = useState<any>(null);
  const [reflect, setReflect] = useState<any>(null);
  const [audit, setAudit] = useState<any[]>([]);
  const [traces, setTraces] = useState<any[]>([]);

  async function refresh() {
    setHz(await healthz().catch(() => null));
    setReflect(await systemReflect().catch(() => null));
    setAudit(await recentAudit().catch(() => []));
    setTraces(await recentTrace().catch(() => []));
  }

  useEffect(() => { refresh(); }, []);

  const tierCounts: Record<string, number> = traces.reduce((acc, t) => {
    const k = String(t.tier ?? 0);
    acc[k] = (acc[k] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <Activity size={18} className="text-neon-lime" />
        <h1 className="font-display text-2xl font-bold">System Health</h1>
        <button className="btn-ghost ml-auto flex items-center gap-2 text-sm" onClick={refresh}>
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      <div className="grid md:grid-cols-3 gap-4 mb-4">
        <div className="glass p-4">
          <div className="text-xs uppercase tracking-widest text-slate-400 mb-2">Backend</div>
          <div className="text-2xl font-display">{hz?.ok ? 'OK' : '—'}</div>
          <div className="text-[11px] text-slate-500 mt-1">v{hz?.version || '—'}</div>
        </div>
        <div className="glass p-4">
          <div className="text-xs uppercase tracking-widest text-slate-400 mb-2">MIRL models</div>
          <div className="space-y-1 text-xs font-mono">
            {hz?.mirl_models && Object.entries<string>(hz.mirl_models).map(([k, v]) => (
              <div key={k} className="flex justify-between"><span className="text-slate-500">{k}</span><span>{v}</span></div>
            ))}
          </div>
        </div>
        <div className="glass p-4">
          <div className="text-xs uppercase tracking-widest text-slate-400 mb-2">Self-reflection (DMN)</div>
          <div className="text-sm text-slate-300 leading-relaxed">{reflect?.content || '—'}</div>
          {reflect?.hints?.length > 0 && (
            <ul className="mt-2 list-disc pl-5 text-xs text-slate-400">
              {reflect.hints.map((h: string, i: number) => <li key={i}>{h}</li>)}
            </ul>
          )}
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass p-4">
          <div className="text-xs uppercase tracking-widest text-slate-400 mb-2">MIRL tier distribution</div>
          <MIRLDistribution counts={tierCounts} />
        </motion.div>

        <div className="glass p-4">
          <div className="text-xs uppercase tracking-widest text-slate-400 mb-2">Guardrail audit (last 8)</div>
          <ul className="space-y-2 text-xs">
            {audit.slice(-8).reverse().map((a, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="chip chip-pink shrink-0">{(a.violations || []).join(', ') || 'event'}</span>
                <span className="text-slate-400 truncate">{a.agent} · {a.phase}</span>
              </li>
            ))}
            {audit.length === 0 && <li className="text-slate-500">No interventions yet — keep going.</li>}
          </ul>
        </div>
      </div>
    </div>
  );
}
