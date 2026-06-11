import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Brain, GraduationCap, Activity, BarChart3, KeyRound, LogOut } from 'lucide-react';
import { useStore } from '../lib/store';

type Props = { onOpenBYOK: () => void };

const links = [
  { to: '/learner', label: 'Learner', icon: GraduationCap },
  { to: '/manager', label: 'Manager', icon: BarChart3 },
  { to: '/system', label: 'System Health', icon: Activity }
];

export default function Sidebar({ onOpenBYOK }: Props) {
  const { setBYOK, byok } = useStore();
  return (
    <aside className="w-64 shrink-0 hidden md:flex flex-col border-r border-white/5 p-5 gap-6 bg-gradient-to-b from-panel/60 to-ink/80 backdrop-blur-xl">
      <div className="flex items-center gap-2">
        <motion.div
          animate={{ rotate: [0, 6, -6, 0] }}
          transition={{ duration: 8, repeat: Infinity }}
          className="w-10 h-10 rounded-xl bg-gradient-to-br from-neon-violet to-neon-cyan shadow-glow flex items-center justify-center"
        >
          <Brain size={22} className="text-ink" />
        </motion.div>
        <div>
          <div className="font-display font-bold text-lg leading-tight">DENDRITE</div>
          <div className="text-[10px] uppercase tracking-widest text-slate-400">Cognitive OS</div>
        </div>
      </div>

      <nav className="flex flex-col gap-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to} to={to}
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition ${
                isActive
                  ? 'bg-gradient-to-r from-neon-violet/20 to-neon-cyan/15 text-white shadow-glow'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`
            }
          >
            <Icon size={16} /> {label}
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto space-y-2">
        <button onClick={onOpenBYOK} className="w-full btn-ghost flex items-center gap-2 justify-center text-sm">
          <KeyRound size={14} />
          {byok ? 'Update Foundry key' : 'Connect Foundry'}
        </button>
        {byok && (
          <button
            onClick={() => setBYOK(null)}
            className="w-full text-xs text-slate-500 hover:text-rose-300 flex items-center gap-1.5 justify-center"
          >
            <LogOut size={12} /> Disconnect
          </button>
        )}
        <div className="text-[10px] text-slate-500 leading-snug">
          All data here is synthetic per the Microsoft Agents League brief.
          You're chatting with AI.
        </div>
      </div>
    </aside>
  );
}
