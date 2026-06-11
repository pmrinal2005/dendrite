import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ZAxis, ResponsiveContainer } from 'recharts';

type Cell = {
  certification: string;
  urgency: number;
  readiness: number;
  learners_at_risk: number;
  total_learners: number;
};

export default function RiskRadar({ data }: { data: Cell[] }) {
  const points = data.map((d) => ({
    x: d.readiness * 100,
    y: d.urgency * 100,
    z: d.learners_at_risk * 200 + 80,
    name: d.certification,
    risk: d.learners_at_risk,
    total: d.total_learners
  }));
  return (
    <div className="w-full h-72">
      <ResponsiveContainer>
        <ScatterChart margin={{ top: 10, right: 30, bottom: 25, left: 0 }}>
          <CartesianGrid stroke="rgba(255,255,255,0.08)" />
          <XAxis type="number" dataKey="x" name="Readiness"
                 domain={[0, 100]} tick={{ fill: '#94a3b8' }}
                 label={{ value: 'Readiness →', position: 'bottom', fill: '#94a3b8' }} />
          <YAxis type="number" dataKey="y" name="Urgency"
                 domain={[0, 100]} tick={{ fill: '#94a3b8' }}
                 label={{ value: 'Urgency ↑', angle: -90, position: 'insideLeft', fill: '#94a3b8' }} />
          <ZAxis dataKey="z" range={[80, 600]} />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            contentStyle={{ background: '#0d1226', border: '1px solid rgba(167,139,250,0.4)', borderRadius: 8 }}
            formatter={(_v: any, _n: any, p: any) => [`${p.payload.risk}/${p.payload.total} at risk`, p.payload.name]}
            labelFormatter={() => ''}
          />
          <Scatter data={points} fill="#f472b6" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
