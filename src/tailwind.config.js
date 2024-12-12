/** @type {import('tailwindcss').Config} */

import defaultTheme from 'tailwindcss/defaultTheme';

export default {
  content: [
      "./c3ds/static/**/*.{vue,js,ts,jsx,tsx}",
      "./c3ds/*/templates/**/*.html",
      "./c3ds/*/static/**/*.{vue,js,ts,jsx,tsx,html}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#ff5053',
        highlight: '#fef2ff',
        accent1: '#6a5fdb',
        accent2: '#b2aaff',
        accent3: '#261a66',
        accent4: '#29114c',
        background: '#0f000a',
      },
      fontFamily: {
        'display-headline': ['Pillow Lava'],
        'headline': ['Space Grotesk'],
        'subheadline': ['Uncut Sans'],
        'sans': ['Uncut Sans', ...defaultTheme.fontFamily.sans],
        'numbers': ['Space Mono']
      },
      gridTemplateColumns: {
        'schedule': 'max-content 15px 1fr',
      }
    },
  },
  plugins: [],
}

