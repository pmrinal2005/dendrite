import { useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, Loader2, AlertTriangle } from 'lucide-react';
import { managerInsights } from '../lib/api';
import RiskRadar from '../components/RiskRadar';

export default function ManagerPage() {
  const [query, setQuery] = useState("Where is TEAM-A's certification risk this quarter?");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);

  async function run() {
    setLoading(true); setErr(null);
    try {
      const r = await managerInsights({ query, team_id: 'TEAM-A' });
      setData(r);
    } catch (e: any) {
      setErr(e.message || 'Manager query failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <BarChart3 size={18} className="text-neon-cyan" />
        <h1 className="font-display text-2xl font-bold">Manager workspace</h1>
        <span className="chip ml-auto">TEAM-A · anonymised aggregates</span>
      </div>

      <div className="glass p-4 mb-4 flex gap-2">
        <input className="flex-1" value={query} onChange={(e) => setQuery(e.target.value)} />
        <button className="btn-primary flex items-center gap-2" onClick={run} disabled={loading}>
          {loading ? <Loader2 size={14} className="animate-spin" /> : null}
          Run Manager Insights
        </button>
      </div>
      {err && <div className="text-rose-300 text-sm mb-3">{err}</div>}

      {data && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
          <div className="glass-strong p-5">
            <div className="font-display text-xl font-bold mb-2">Summary</div>
            <div className="text-slate-300 text-[15px] leading-relaxed">{data.summary}</div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="glass p-4">
              <div className="text-xs uppercase tracking-widest text-slate-400 mb-2">Workforce Risk Radar</div>
              {data.risk_radar?.length ? <RiskRadar data={data.risk_radar} /> :
                <div className="text-sm text-slate-500">No risk cells.</div>}
            </div>
            <div className="glass p-4">
              <div className="text-xs uppercase tracking-widest text-slate-400 mb-3">Capability Coverage</div>
              <div className="space-y-2">
                {Object.entries<number>(data.coverage_map || {}).map(([k, v]) => (
                  <div key={k}>
                    <div className="flex justify-between text-sm"><span>{k}</span>
                      <span className="text-slate-400">{Math.round(v * 100)}%</span></div>
                    <div className="h-2 rounded-full bg-white/5 overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-neon-violet to-neon-cyan"
                           style={{ width: `${v * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {data.bus_factor_alerts?.length > 0 && (
            <div className="glass p-4">
              <div className="text-xs uppercase tracking-widest text-slate-400 mb-3">Bus Factor Alerts</div>
              <ul className="space-y-2 text-sm">
                {data.bus_factor_alerts.map((b: string, i: number) => (
                  <li key={i} className="flex items-start gap-2 text-amber-200">
                    <AlertTriangle size={14} className="mt-0.5" /> {b}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {data.recommended_actions?.length > 0 && (
            <div className="glass p-4">
              <div className="text-xs uppercase tracking-widest text-slate-400 mb-3">Recommended actions</div>
              <ol className="space-y-2 text-sm list-decimal pl-5 text-slate-200">
                {data.recommended_actions.map((a: string, i: number) => <li key={i}>{a}</li>)}
              </ol>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}
