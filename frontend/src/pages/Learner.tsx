import { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, ChevronRight, Loader2, CheckCircle2, XCircle } from 'lucide-react';
import ChatPanel from '../components/ChatPanel';
import ReadinessGauge from '../components/ReadinessGauge';
import WeaknessRadar from '../components/WeaknessRadar';
import { generateAssessment, scoreAssessment } from '../lib/api';

type Q = {
  id: string;
  skill_area: string;
  difficulty: number;
  prompt: string;
  options: string[];
  correct_index: number;
  citation: { doc: string; section?: string };
  rationale: string;
};

export default function LearnerPage() {
  const [tab, setTab] = useState<'chat' | 'assess'>('chat');
  const [qs, setQs] = useState<Q[]>([]);
  const [answers, setAnswers] = useState<Record<string, { chosen: number; confidence: number }>>({});
  const [loading, setLoading] = useState(false);
  const [score, setScore] = useState<any>(null);

  async function loadAssessment() {
    setLoading(true); setScore(null);
    try {
      const r = await generateAssessment({
        certification: 'AZ-204',
        skill_areas: ['API Development', 'Azure Functions', 'Storage'],
        num_questions: 5
      });
      setQs(r.questions || []);
      setAnswers({});
    } finally {
      setLoading(false);
    }
  }

  async function submitAll() {
    setLoading(true);
    try {
      const payload = {
        certification: 'AZ-204',
        answers: qs.map((q) => ({
          question_id: q.id,
          chosen_index: answers[q.id]?.chosen ?? 0,
          confidence: answers[q.id]?.confidence ?? 0.5
        })),
        questions: qs
      };
      const r = await scoreAssessment(payload);
      setScore(r);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid lg:grid-cols-[1fr_320px] gap-4 h-full">
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Brain size={18} className="text-neon-violet" />
          <h1 className="font-display text-2xl font-bold">Learner workspace</h1>
          <span className="chip ml-auto">L-1001 · Cloud Engineer · AZ-204</span>
        </div>

        <div className="flex gap-1 mb-3">
          {(['chat', 'assess'] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-3 py-1.5 rounded-lg text-sm transition ${
                tab === t
                  ? 'bg-gradient-to-r from-neon-violet/25 to-neon-cyan/15 text-white'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {t === 'chat' ? '💬 Conversation' : '🎯 Adaptive Assessment'}
            </button>
          ))}
        </div>

        {tab === 'chat' && <ChatPanel persona="learner" />}

        {tab === 'assess' && (
          <div className="glass p-4 space-y-4">
            <div className="flex items-center gap-3">
              <button onClick={loadAssessment} className="btn-primary flex items-center gap-2" disabled={loading}>
                {loading ? <Loader2 size={14} className="animate-spin" /> : <ChevronRight size={14} />}
                {qs.length ? 'Regenerate' : 'Generate citation-grounded assessment'}
              </button>
              {qs.length > 0 && !score && (
                <button onClick={submitAll} className="btn-ghost" disabled={loading}>
                  Submit answers
                </button>
              )}
            </div>

            {qs.map((q, i) => {
              const a = answers[q.id];
              const correct = score && a?.chosen === q.correct_index;
              return (
                <motion.div
                  key={q.id}
                  initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                  className="glass p-4"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className="chip chip-cyan">{q.skill_area}</span>
                    <span className="chip">difficulty {Math.round(q.difficulty * 100)}%</span>
                    <span className="ml-auto text-xs text-slate-500">Q{i + 1}</span>
                  </div>
                  <div className="font-medium mb-3">{q.prompt}</div>
                  <div className="grid sm:grid-cols-2 gap-2">
                    {q.options.map((opt, idx) => {
                      const chosen = a?.chosen === idx;
                      const showCorrect = score && idx === q.correct_index;
                      const showWrong = score && chosen && idx !== q.correct_index;
                      return (
                        <button
                          key={idx}
                          onClick={() => setAnswers((x) => ({
                            ...x, [q.id]: { chosen: idx, confidence: a?.confidence ?? 0.5 }
                          }))}
                          className={`text-left rounded-lg px-3 py-2 text-sm border transition ${
                            showCorrect ? 'border-emerald-400/60 bg-emerald-400/10'
                              : showWrong ? 'border-rose-400/60 bg-rose-400/10'
                              : chosen ? 'border-neon-violet/60 bg-neon-violet/10'
                              : 'border-white/10 hover:border-white/30'
                          }`}
                        >
                          {opt}
                          {showCorrect && <CheckCircle2 className="inline ml-1.5 text-emerald-300" size={14} />}
                          {showWrong   && <XCircle      className="inline ml-1.5 text-rose-300"    size={14} />}
                        </button>
                      );
                    })}
                  </div>

                  {!score && a && (
                    <div className="mt-3 text-xs text-slate-400">
                      How confident? <input
                        type="range" min={0} max={100} value={Math.round((a.confidence ?? 0.5) * 100)}
                        onChange={(e) => setAnswers((x) => ({
                          ...x, [q.id]: { chosen: a.chosen, confidence: Number(e.target.value) / 100 }
                        }))}
                        className="align-middle mx-2"
                      /> {Math.round((a.confidence ?? 0.5) * 100)}%
                    </div>
                  )}

                  {score && (
                    <div className="mt-3 text-xs text-slate-400">
                      <em>{q.rationale}</em>
                      <div className="mt-1">Cite: <span className="chip chip-cyan">{q.citation.doc}</span></div>
                    </div>
                  )}
                </motion.div>
              );
            })}

            {score && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-strong p-5">
                <div className="font-display text-xl font-bold mb-2">Weakness Fingerprint</div>
                <div className="grid md:grid-cols-2 gap-4">
                  <ReadinessGauge value={score.readiness_pct} label={`Knowledge: ${score.knowledge_temperature}`} />
                  <WeaknessRadar data={score.fingerprint} />
                </div>
                <div className="mt-4 text-sm">
                  <div className="font-semibold mb-1">Next action</div>
                  <div className="text-slate-300">{score.next_action}</div>
                  {score.socratic_followups?.length > 0 && (
                    <div className="mt-3">
                      <div className="font-semibold mb-1">Socratic follow-ups</div>
                      <ul className="list-disc pl-5 text-slate-400">
                        {score.socratic_followups.map((s: string, i: number) => <li key={i}>{s}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </div>
        )}
      </div>

      <aside className="hidden lg:block">
        <div className="glass p-4 mb-3">
          <div className="text-xs uppercase tracking-widest text-slate-400 mb-2">Today</div>
          <ReadinessGauge value={score?.readiness_pct ?? 64} />
        </div>
        <div className="glass p-4">
          <div className="text-xs uppercase tracking-widest text-slate-400 mb-2">Brain regions live</div>
          <ul className="space-y-1.5 text-sm">
            {[
              ['Prefrontal', 'planning'],
              ['Hippocampus', 'grounding'],
              ['Cerebellum', 'scheduling'],
              ['Amygdala', 'tone-tuning'],
              ['Immune', 'guardrails'],
              ['DMN', 'self-reflection']
            ].map(([k, v]) => (
              <li key={k} className="flex justify-between">
                <span className="text-slate-300">{k}</span>
                <span className="text-slate-500 text-xs">{v}</span>
              </li>
            ))}
          </ul>
        </div>
      </aside>
    </div>
  );
}
