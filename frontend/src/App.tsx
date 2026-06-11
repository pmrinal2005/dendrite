import { useState } from 'react';
import { Route, Routes, Navigate } from 'react-router-dom';
import NeuralBackground from './components/NeuralBackground';
import Sidebar from './components/Sidebar';
import BYOKModal from './components/BYOKModal';
import Landing from './pages/Landing';
import Learner from './pages/Learner';
import Manager from './pages/Manager';
import SystemHealth from './pages/SystemHealth';
import { useStore } from './lib/store';

export default function App() {
  const [byokOpen, setBYOKOpen] = useState(false);
  const ready = useStore((s) => s.ready);

  // public landing always
  return (
    <>
      <NeuralBackground />
      <BYOKModal open={byokOpen} onClose={() => setBYOKOpen(false)} />

      <Routes>
        <Route path="/" element={<Landing onOpenBYOK={() => setBYOKOpen(true)} />} />

        <Route
          path="/*"
          element={
            <div className="min-h-screen flex">
              <Sidebar onOpenBYOK={() => setBYOKOpen(true)} />
              <main className="flex-1 p-6 max-w-[1400px] mx-auto">
                {!ready ? (
                  <div className="glass-strong max-w-xl mx-auto p-8 text-center">
                    <div className="text-2xl font-display font-bold mb-2">Connect your Foundry to continue</div>
                    <p className="text-slate-400 text-sm mb-5">
                      DENDRITE is BYOK — your Foundry endpoint + key live only in your browser.
                    </p>
                    <button className="btn-primary" onClick={() => setBYOKOpen(true)}>
                      Connect Foundry
                    </button>
                  </div>
                ) : (
                  <Routes>
                    <Route path="/learner" element={<Learner />} />
                    <Route path="/manager" element={<Manager />} />
                    <Route path="/system" element={<SystemHealth />} />
                    <Route path="*" element={<Navigate to="/learner" replace />} />
                  </Routes>
                )}
              </main>
            </div>
          }
        />
      </Routes>
    </>
  );
}
