/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      animation: {
        'pulse-border': 'pulse-border 2s infinite',
      },
      keyframes: {
        'pulse-border': {
          '0%, 100%': { borderColor: '#3b82f6' },
          '50%': { borderColor: '#1d4ed8' },
        }
      }
    },
  },
  plugins: [],
}