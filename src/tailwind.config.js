/** @type {import('tailwindcss').Config} */
export default {
  content: [
      "./c3ds/static/**/*.{vue,js,ts,jsx,tsx}",
      "./c3ds/*/templates/**/*.html",
      "./c3ds/*/static/**/*.{vue,js,ts,jsx,tsx,html}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

