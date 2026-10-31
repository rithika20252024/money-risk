/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: {
          50: '#FDFBF7',
          100: '#FAF7F2',
          200: '#F4EFEA',
          300: '#EBE3D7',
          400: '#DDD2C3',
          500: '#C8B8A4',
          600: '#A9947E',
          700: '#84705C',
          800: '#5F4F3F',
          900: '#3D3126',
        },
        espresso: {
          900: '#1C1917',
          800: '#292524',
          700: '#44403C',
          500: '#78716C',
        }
      }
    },
  },
  plugins: [],
}
