import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell, Tooltip } from 'recharts';
import { tierColor, tierLabel } from '../lib/utils';

export default function MIRLDistribution({ counts }: { counts: Record<string, number> }) {
  const data = [1, 2, 3, 4, 5].map((t) => ({
    tier: tierLabel(t),
    count: counts[t] || counts[String(t)] || 0,
    color: tierColor(t)
  }));
  return (
    <div className="w-full h-60">
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 10, right: 10, bottom: 5, left: 0 }}>
          <XAxis dataKey="tier" tick={{ fill: '#94a3b8', fontSize: 11 }} />
          <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} allowDecimals={false} />
          <Tooltip
            contentStyle={{ background: '#0d1226', border: '1px solid rgba(167,139,250,0.4)', borderRadius: 8 }}
          />
          <Bar dataKey="count" radius={[8, 8, 0, 0]}>
            {data.map((d, i) => <Cell key={i} fill={d.color} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
