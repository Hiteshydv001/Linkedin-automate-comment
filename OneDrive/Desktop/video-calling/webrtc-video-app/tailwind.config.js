/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      animation: {
        'join': 'join 0.5s ease-in-out',
      },
      keyframes: {
        join: {
          '0%': { transform: 'scale(0.8)', opacity: '0', filter: 'blur(4px)' },
          '100%': { transform: 'scale(1)', opacity: '1', filter: 'blur(0)' },
        },
      },
    },
  },
  plugins: [],
};