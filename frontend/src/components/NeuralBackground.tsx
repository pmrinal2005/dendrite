import { useEffect, useRef } from 'react';

/**
 * Lightweight neural-network animation drawn on a single canvas.
 * Designed to run smoothly on a low-end laptop:
 *  - particle count adapts to screen width
 *  - capped at 30 fps via setTimeout
 *  - no per-particle DOM nodes
 */
export default function NeuralBackground() {
  const ref = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = ref.current!;
    const ctx = canvas.getContext('2d')!;
    let raf = 0;
    let last = 0;

    type P = { x: number; y: number; vx: number; vy: number };
    let particles: P[] = [];

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      canvas.style.width = window.innerWidth + 'px';
      canvas.style.height = window.innerHeight + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const target = Math.min(80, Math.floor(window.innerWidth / 22));
      particles = Array.from({ length: target }, () => ({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        vx: (Math.random() - 0.5) * 0.35,
        vy: (Math.random() - 0.5) * 0.35
      }));
    };
    resize();
    window.addEventListener('resize', resize);

    const tick = (t: number) => {
      if (t - last < 33) {
        raf = requestAnimationFrame(tick);
        return;
      }
      last = t;
      ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
      // soft vignette
      const g = ctx.createRadialGradient(
        window.innerWidth * 0.5, window.innerHeight * 0.55, 80,
        window.innerWidth * 0.5, window.innerHeight * 0.55, Math.max(window.innerWidth, window.innerHeight)
      );
      g.addColorStop(0, 'rgba(167,139,250,0.06)');
      g.addColorStop(1, 'rgba(7,11,24,0)');
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);

      // move + draw nodes
      for (const p of particles) {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > window.innerWidth) p.vx *= -1;
        if (p.y < 0 || p.y > window.innerHeight) p.vy *= -1;
      }
      // edges
      ctx.lineWidth = 1;
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const a = particles[i], b = particles[j];
          const dx = a.x - b.x, dy = a.y - b.y;
          const d2 = dx * dx + dy * dy;
          if (d2 < 130 * 130) {
            const alpha = 1 - Math.sqrt(d2) / 130;
            ctx.strokeStyle = `rgba(167,139,250,${alpha * 0.35})`;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        }
      }
      // nodes
      for (const p of particles) {
        ctx.fillStyle = 'rgba(34,211,238,0.85)';
        ctx.beginPath();
        ctx.arc(p.x, p.y, 1.6, 0, Math.PI * 2);
        ctx.fill();
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas
      ref={ref}
      aria-hidden="true"
      className="fixed inset-0 -z-10 pointer-events-none"
    />
  );
}
