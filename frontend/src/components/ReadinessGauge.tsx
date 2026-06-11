import { RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer } from 'recharts';

export default function ReadinessGauge({ value, label }: { value: number; label?: string }) {
  const data = [{ name: 'r', value }];
  return (
    <div className="relative w-full h-44">
      <ResponsiveContainer>
        <RadialBarChart innerRadius="70%" outerRadius="100%" data={data} startAngle={210} endAngle={-30}>
          <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
          <RadialBar dataKey="value" cornerRadius={10} fill="url(#g)" background={{ fill: '#1f2547' }} />
          <defs>
            <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#a78bfa" />
              <stop offset="100%" stopColor="#22d3ee" />
            </linearGradient>
          </defs>
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="text-3xl font-display font-bold">{Math.round(value)}%</div>
        <div className="text-[10px] uppercase tracking-widest text-slate-400">{label || 'Readiness'}</div>
      </div>
    </div>
  );
}
