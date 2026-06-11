import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

type Cell = { skill_area: string; mastery_pct: number; state: string };

export default function WeaknessRadar({ data }: { data: Cell[] }) {
  const chartData = data.map((d) => ({ subject: d.skill_area, A: d.mastery_pct }));
  return (
    <div className="w-full h-64">
      <ResponsiveContainer>
        <RadarChart data={chartData} outerRadius="78%">
          <PolarGrid stroke="rgba(255,255,255,0.1)" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: '#cbd5e1', fontSize: 11 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} stroke="rgba(255,255,255,0.1)" />
          <Radar dataKey="A" stroke="#a78bfa" fill="#a78bfa" fillOpacity={0.35} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
