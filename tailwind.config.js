/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        tactical: {
          primary: '#1a1a2e',
          secondary: '#16213e',
          accent: '#0f3460',
          danger: '#e53e3e',
          warning: '#dd6b20',
          success: '#38a169',
          info: '#3182ce',
        },
        military: {
          dark: '#0d1117',
          gray: '#161b22',
          light: '#21262d',
          border: '#30363d',
          text: '#f0f6fc',
          muted: '#8b949e',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Monaco', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
      boxShadow: {
        'tactical': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
        'glow': '0 0 20px rgba(59, 130, 246, 0.5)',
        'danger-glow': '0 0 20px rgba(229, 62, 62, 0.5)',
      }
    },
  },
  plugins: [],
}
