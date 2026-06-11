import { motion } from 'framer-motion';
import { tierColor, tierLabel } from '../lib/utils';
import type { AgentOutput } from '../lib/api';
import { ShieldAlert } from 'lucide-react';

type Props = { trace: AgentOutput[]; guardrail?: { intervened: boolean; violations: string[]; note?: string } };

export default function AgentTrace({ trace, guardrail }: Props) {
  if (!trace?.length) return null;
  return (
    <div className="glass p-4 mt-3">
      <div className="text-xs uppercase tracking-widest text-slate-400 mb-3">
        🧠 Cognitive trace
      </div>
      <div className="flex flex-wrap gap-2">
        {trace.map((t, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-white/5 border border-white/10"
            title={`confidence ${(t.confidence * 100).toFixed(0)}%`}
          >
            <span
              className="w-2 h-2 rounded-full"
              style={{ background: tierColor(t.tier), boxShadow: `0 0 10px ${tierColor(t.tier)}` }}
            />
            <span className="text-sm font-medium">{t.agent}</span>
            <span className="text-[10px] text-slate-400">{tierLabel(t.tier)}</span>
            <span className="text-[10px] text-slate-500">·</span>
            <span className="text-[10px] text-slate-400">conf {(t.confidence * 100).toFixed(0)}%</span>
            {t.extra?.critic_verdict && (
              <span className="chip chip-pink ml-1">Critic: {t.extra.critic_verdict}</span>
            )}
          </motion.div>
        ))}
      </div>
      {guardrail?.intervened && (
        <div className="mt-3 flex items-start gap-2 text-xs text-amber-300">
          <ShieldAlert size={14} className="mt-0.5" />
          <div>{guardrail.note} · violations: {guardrail.violations.join(', ')}</div>
        </div>
      )}
    </div>
  );
}
