/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        /* Linear-style design tokens */
        background: {
          DEFAULT: '#0f0f10',   // base dark
          subtle: '#141415',
          elevated: '#1a1a1b',
          overlay: '#202022',
        },
        surface: {
          DEFAULT: '#1c1c1e',
          hover: '#242426',
          active: '#2a2a2c',
          border: '#2e2e30',
        },
        brand: {
          DEFAULT: '#5e6ad2',   // indigo accent (Linear)
          hover: '#6b77e0',
          active: '#4f5ab8',
          muted: 'rgba(94,106,210,0.15)',
        },
        text: {
          primary: '#e8e8ea',
          secondary: '#8a8a8f',
          tertiary: '#55555a',
          disabled: '#3a3a3d',
          inverse: '#0f0f10',
        },
        status: {
          success: '#3dd68c',
          warning: '#f5a623',
          error: '#e5484d',
          info: '#5e6ad2',
        },
        room: {
          online: '#3dd68c',
          away: '#f5a623',
          offline: '#55555a',
        },
      },
      borderRadius: {
        sm: '4px',
        DEFAULT: '6px',
        md: '8px',
        lg: '12px',
        xl: '16px',
      },
      boxShadow: {
        card: '0 0 0 1px rgba(255,255,255,0.06), 0 4px 16px rgba(0,0,0,0.4)',
        popup: '0 0 0 1px rgba(255,255,255,0.08), 0 8px 32px rgba(0,0,0,0.6)',
        glow: '0 0 20px rgba(94,106,210,0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.15s ease',
        'slide-up': 'slideUp 0.2s ease',
        'pulse-dot': 'pulseDot 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: 0 }, to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: 'translateY(6px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        pulseDot: { '0%,100%': { opacity: 1 }, '50%': { opacity: 0.4 } },
      },
    },
  },
  plugins: [],
}
