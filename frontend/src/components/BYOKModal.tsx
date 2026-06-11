import { motion, AnimatePresence } from 'framer-motion';
import { KeyRound, Sparkles, X, ShieldCheck } from 'lucide-react';
import { useState } from 'react';
import { useStore } from '../lib/store';

type Props = { open: boolean; onClose: () => void };

export default function BYOKModal({ open, onClose }: Props) {
  const { byok, setBYOK } = useStore();
  const [endpoint, setEndpoint] = useState(byok?.endpoint || '');
  const [key, setKey] = useState(byok?.key || '');
  const [kbAgentId, setKbAgentId] = useState(byok?.kbAgentId || '');
  const [fabricWS, setFabricWS] = useState(byok?.fabricWorkspaceId || '');
  const [fabricOnt, setFabricOnt] = useState(byok?.fabricOntologyId || '');
  const [backend, setBackend] = useState(byok?.backendBase || 'http://localhost:8000');

  function save() {
    setBYOK({
      endpoint, key,
      kbAgentId: kbAgentId || undefined,
      fabricWorkspaceId: fabricWS || undefined,
      fabricOntologyId: fabricOnt || undefined,
      backendBase: backend
    });
    onClose();
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
        >
          <motion.div
            className="glass-strong w-full max-w-2xl p-7 relative"
            initial={{ y: 24, opacity: 0, scale: 0.97 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            exit={{ y: 24, opacity: 0, scale: 0.97 }}
            transition={{ type: 'spring', stiffness: 240, damping: 22 }}
          >
            <button
              onClick={onClose}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
              aria-label="close"
            ><X size={20} /></button>

            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-neon-violet to-neon-cyan flex items-center justify-center shadow-glow">
                <KeyRound size={20} className="text-ink" />
              </div>
              <div>
                <h2 className="font-display text-2xl font-bold">Connect your Foundry</h2>
                <p className="text-sm text-slate-400">
                  BYOK — your keys live only in this browser. DENDRITE never stores them.
                </p>
              </div>
            </div>

            <div className="grid sm:grid-cols-2 gap-3 mt-4">
              <label className="sm:col-span-2 text-sm">
                <span className="text-slate-300 flex items-center gap-1.5">
                  <Sparkles size={14} className="text-neon-violet" />
                  Foundry project endpoint
                </span>
                <input
                  className="w-full mt-1"
                  placeholder="https://<resource>.services.ai.azure.com/api/projects/dendrite"
                  value={endpoint}
                  onChange={(e) => setEndpoint(e.target.value)}
                />
              </label>

              <label className="sm:col-span-2 text-sm">
                <span className="text-slate-300">API key</span>
                <input
                  className="w-full mt-1"
                  type="password"
                  placeholder="Paste your Foundry key"
                  value={key}
                  onChange={(e) => setKey(e.target.value)}
                />
              </label>

              <label className="text-sm">
                <span className="text-slate-300">Foundry IQ KB Agent ID <em className="text-slate-500">(optional)</em></span>
                <input
                  className="w-full mt-1"
                  placeholder="asst_…"
                  value={kbAgentId}
                  onChange={(e) => setKbAgentId(e.target.value)}
                />
              </label>

              <label className="text-sm">
                <span className="text-slate-300">Backend URL</span>
                <input
                  className="w-full mt-1"
                  value={backend}
                  onChange={(e) => setBackend(e.target.value)}
                />
              </label>

              <label className="text-sm">
                <span className="text-slate-300">Fabric Workspace ID <em className="text-slate-500">(optional)</em></span>
                <input className="w-full mt-1" value={fabricWS} onChange={(e) => setFabricWS(e.target.value)} />
              </label>

              <label className="text-sm">
                <span className="text-slate-300">Fabric Ontology ID <em className="text-slate-500">(optional)</em></span>
                <input className="w-full mt-1" value={fabricOnt} onChange={(e) => setFabricOnt(e.target.value)} />
              </label>
            </div>

            <div className="mt-5 flex items-center gap-2 text-xs text-slate-400">
              <ShieldCheck size={14} className="text-neon-lime" />
              Stored in <span className="font-mono">localStorage</span> only. Cleared on logout.
            </div>

            <div className="mt-6 flex justify-end gap-2">
              <button className="btn-ghost" onClick={onClose}>Cancel</button>
              <button
                className="btn-primary"
                onClick={save}
                disabled={!endpoint || !key}
              >Connect</button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
