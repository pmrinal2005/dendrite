import { useState } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader2, Sparkles } from 'lucide-react';
import { chat, type ChatResponse } from '../lib/api';
import AgentTrace from './AgentTrace';

type Msg = { role: 'user' | 'assistant'; text: string; resp?: ChatResponse };

const QUICK = [
  'I want AZ-204 in 6 weeks — I am a Cloud Engineer with heavy Tue/Thu meetings.',
  'Give me a study plan based on my work pattern.',
  'Show me a 5-question assessment for AZ-204.',
  'How is my team doing on certifications?',
  'Is my AZ-204 cert still fresh after 4 months?'
];

export default function ChatPanel({ persona }: { persona: 'learner' | 'manager' }) {
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function send(text?: string) {
    const m = (text ?? input).trim();
    if (!m) return;
    setMsgs((x) => [...x, { role: 'user', text: m }]);
    setInput(''); setErr(null); setLoading(true);
    try {
      const resp = await chat({
        message: m,
        persona,
        learner_id: persona === 'learner' ? 'L-1001' : undefined,
        role: persona === 'learner' ? 'Cloud Engineer' : undefined,
        target_certification: persona === 'learner' ? 'AZ-204' : undefined,
        weeks_available: 6
      });
      setMsgs((x) => [...x, { role: 'assistant', text: resp.reply, resp }]);
    } catch (e: any) {
      setErr(e.message || 'Request failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="glass p-4 flex flex-col h-[calc(100vh-160px)]">
      <div className="flex flex-wrap gap-2 mb-3">
        {QUICK.map((q, i) => (
          <button key={i} onClick={() => send(q)} className="chip">
            <Sparkles size={12} /> {q}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto scroll-thin pr-2 space-y-4">
        {msgs.length === 0 && (
          <div className="h-full grid place-items-center text-center text-slate-400 px-6">
            <div>
              <div className="text-3xl font-display font-bold text-white mb-2">
                Welcome to <span className="bg-gradient-to-r from-neon-violet to-neon-cyan bg-clip-text text-transparent">DENDRITE</span>
              </div>
              <p className="max-w-md text-sm leading-relaxed">
                10 specialised agents — Prefrontal Cortex, Hippocampus, Amygdala, Default Mode Network — reason together to plan, assess, and protect your certification journey. Pick a prompt above or type your own.
              </p>
            </div>
          </div>
        )}

        {msgs.map((m, i) => (
          <motion.div
            key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
            className={m.role === 'user' ? 'flex justify-end' : ''}
          >
            <div className={
              m.role === 'user'
                ? 'max-w-[80%] bg-gradient-to-br from-neon-violet/20 to-neon-cyan/15 border border-neon-violet/30 rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm'
                : 'max-w-[88%] glass px-4 py-3 prose-dendrite text-[15px] whitespace-pre-wrap'
            }>
              {m.text.split('\n').map((line, idx) => (
                <div key={idx} dangerouslySetInnerHTML={{ __html: renderInline(line) }} />
              ))}
              {m.resp && (
                <>
                  <AgentTrace trace={m.resp.trace} guardrail={m.resp.guardrail} />
                  {m.resp.citations.length > 0 && (
                    <div className="mt-2 text-xs text-slate-400">
                      Citations: {m.resp.citations.map((c, k) => (
                        <span key={k} className="chip chip-cyan mr-1">{c.doc}</span>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          </motion.div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-slate-400 text-sm">
            <Loader2 size={14} className="animate-spin" /> reasoning across agents…
          </div>
        )}
        {err && <div className="text-rose-300 text-sm">{err}</div>}
      </div>

      <div className="mt-3 flex gap-2">
        <input
          className="flex-1"
          placeholder="Ask DENDRITE anything about your certification journey…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') send(); }}
        />
        <button className="btn-primary flex items-center gap-1.5" onClick={() => send()} disabled={loading}>
          <Send size={14} /> Send
        </button>
      </div>
    </div>
  );
}

function renderInline(line: string): string {
  // very small markdown: **bold**, *italic*, `code`
  return line
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code class="font-mono text-xs bg-white/5 px-1.5 rounded">$1</code>');
}
