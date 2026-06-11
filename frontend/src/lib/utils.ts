export function cx(...c: (string | false | undefined | null)[]): string {
  return c.filter(Boolean).join(' ');
}

export function tierColor(tier: number): string {
  return ['#94a3b8', '#22d3ee', '#a78bfa', '#f472b6', '#fb923c', '#a3e635'][tier] || '#94a3b8';
}

export function tierLabel(tier: number): string {
  return [
    'unknown', 'T1 Instant', 'T2 CoT', 'T3 Interleaved', 'T4 Deep', 'T5 Swarm'
  ][tier] || 'unknown';
}

export function pct(x: number): string { return `${Math.round(x * 100)}%`; }
