/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#070b18',
        panel: '#0d1226',
        panel2: '#141a36',
        neon: {
          violet: '#a78bfa',
          cyan: '#22d3ee',
          pink: '#f472b6',
          lime: '#a3e635'
        }
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace']
      },
      boxShadow: {
        glow: '0 0 40px -10px rgba(167,139,250,0.6)',
        glow2: '0 0 60px -10px rgba(34,211,238,0.45)'
      },
      animation: {
        floaty: 'floaty 6s ease-in-out infinite',
        pulseGlow: 'pulseGlow 3s ease-in-out infinite'
      },
      keyframes: {
        floaty: {
          '0%,100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-6px)' }
        },
        pulseGlow: {
          '0%,100%': { boxShadow: '0 0 20px rgba(167,139,250,0.35)' },
          '50%':     { boxShadow: '0 0 40px rgba(167,139,250,0.7)'  }
        }
      }
    }
  },
  plugins: []
};
