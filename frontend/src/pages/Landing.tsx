import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Brain, Sparkles, ShieldCheck, Zap, KeyRound, ArrowRight } from 'lucide-react';

type Props = { onOpenBYOK: () => void };

const AGENTS = [
  ['🧠', 'Meta-Orchestrator', 'Prefrontal Cortex'],
  ['📚', 'Path Curator', 'Hippocampus'],
  ['📅', 'Plan Generator', 'Cerebellum'],
  ['🔔', 'Engagement', 'Motor + Amygdala'],
  ['🎯', 'Assessment', 'Hippocampus + Cerebellum'],
  ['📊', 'Manager Insights', 'Cerebellum'],
  ['🛡️', 'Guardrail', 'Immune System'],
  ['🔁', 'Critic', 'Basal Ganglia'],
  ['🕐', 'Skill Decay', 'Reticular Formation'],
  ['🧠💭', 'Meta-Learning', 'Default Mode Network']
];

const PILLARS = [
  { icon: Brain,       title: '10-agent Nervous System',   sub: 'Each agent maps to a brain region — not branding, design.' },
  { icon: Zap,         title: '5-tier MIRL routing',       sub: 'Phi-4 → gpt-4o-mini → gpt-4.1-mini → o4-mini — costs collapse 5×.' },
  { icon: ShieldCheck, title: 'Silent guardrail',          sub: '6-dimension checks + full audit trail on every output.' },
  { icon: Sparkles,    title: 'Self-improving',            sub: 'Meta-Learning DMN agent reflects on outcomes and tunes itself.' }
];

export default function Landing({ onOpenBYOK }: Props) {
  const nav = useNavigate();
  return (
    <div className="min-h-screen px-6 md:px-16 pt-12 pb-24 max-w-7xl mx-auto">
      <header className="flex items-center justify-between mb-16">
        <div className="flex items-center gap-2.5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-neon-violet to-neon-cyan shadow-glow flex items-center justify-center">
            <Brain size={22} className="text-ink" />
          </div>
          <div>
            <div className="font-display font-bold text-lg leading-tight">DENDRITE</div>
            <div className="text-[10px] uppercase tracking-widest text-slate-400">Cognitive OS</div>
          </div>
        </div>
        <button onClick={onOpenBYOK} className="btn-ghost flex items-center gap-2">
          <KeyRound size={14} /> Connect Foundry
        </button>
      </header>

      <section className="grid md:grid-cols-2 gap-10 items-center mb-24">
        <div>
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <div className="chip mb-5"><Sparkles size={12} /> Microsoft Agents League · Reasoning Agents · Battle #2</div>
            <h1 className="font-display font-bold text-5xl md:text-6xl leading-[1.05] tracking-tight">
              A <span className="bg-gradient-to-r from-neon-violet via-neon-pink to-neon-cyan bg-clip-text text-transparent">cognitive nervous system</span> for enterprise certification learning.
            </h1>
            <p className="text-slate-300/90 mt-6 text-lg max-w-xl leading-relaxed">
              10 specialised agents reason together over Microsoft Foundry IQ, Fabric IQ, and Work IQ —
              orchestrating cognitive readiness at the speed of business.
            </p>
            <div className="mt-8 flex gap-3">
              <button onClick={() => nav('/learner')} className="btn-primary flex items-center gap-2">
                Enter as Learner <ArrowRight size={16} />
              </button>
              <button onClick={() => nav('/manager')} className="btn-ghost">Manager view</button>
            </div>
            <div className="mt-6 text-xs text-slate-500">
              BYOK · Synthetic data only · No server-side secrets · Total Foundry spend ~$11
            </div>
          </motion.div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          {AGENTS.map(([emoji, name, region], i) => (
            <motion.div
              key={name}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 * i }}
              className="glass p-4 flex items-center gap-3"
            >
              <div className="text-2xl">{emoji}</div>
              <div>
                <div className="font-semibold text-sm">{name}</div>
                <div className="text-[11px] text-slate-400">{region}</div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      <section className="grid md:grid-cols-4 gap-4 mb-24">
        {PILLARS.map(({ icon: Icon, title, sub }, i) => (
          <motion.div
            key={title}
            initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06 }}
            className="glass p-5 hover:shadow-glow transition"
          >
            <Icon size={22} className="text-neon-cyan mb-3" />
            <div className="font-semibold mb-1.5">{title}</div>
            <div className="text-sm text-slate-400 leading-relaxed">{sub}</div>
          </motion.div>
        ))}
      </section>

      <section className="glass p-8 mb-16">
        <div className="font-display text-2xl font-bold mb-2">Cost-optimised by design</div>
        <div className="text-slate-400 max-w-3xl text-sm mb-6">
          DENDRITE's MIRL router scores each request 0–100 and dispatches to the cheapest model that can still reason adequately. ~80% of requests land on Tier 1 / 2.
        </div>
        <div className="grid md:grid-cols-5 gap-3 text-sm">
          {[
            ['T1 · Instant',      'Phi-4-mini-instruct', '~$0.00',                  'Routing · FAQ · nudges'],
            ['T2 · CoT',          'gpt-4o-mini',         '$0.15 / $0.60 per 1M',    'Plans · gap detection'],
            ['T3 · Interleaved',  'gpt-4.1-mini',        '$0.40 / $1.60 per 1M',    'Path curation · assessments'],
            ['T4 · Deep',         'o4-mini',             '$1.10 / $4.40 per 1M',    'Critic · scoring'],
            ['T5 · Swarm',        'mixed',               'optimised fan-out',       'Team-scale insights']
          ].map(([t, m, c, u]) => (
            <div key={t} className="glass p-3">
              <div className="text-xs uppercase text-slate-400 tracking-widest mb-1">{t}</div>
              <div className="font-mono text-sm">{m}</div>
              <div className="text-[11px] text-neon-cyan mt-1">{c}</div>
              <div className="text-[11px] text-slate-400 mt-1">{u}</div>
            </div>
          ))}
        </div>
      </section>

      <footer className="text-center text-xs text-slate-500">
        Built for the Microsoft Agents League · DENDRITE © {new Date().getFullYear()}
      </footer>
    </div>
  );
}
