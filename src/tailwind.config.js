/** @type {import('tailwindcss').Config} */

import defaultTheme from 'tailwindcss/defaultTheme';

export default {
  content: [
      "./c3ds/static/**/*.{vue,js,ts,jsx,tsx}",
      "./c3ds/*/templates/**/*.html",
      "./c3ds/*/static/**/*.{vue,js,ts,jsx,tsx,html}",
  ],
  safelist: [
    {
      pattern: /m-(1|2|3|4|5|6|7|8)/, // You can display all the colors that you need
      variants: ['lg', 'hover', 'focus', 'lg:hover'],      // Optional
    },
    {
      pattern: /text-(1|2|3|4|5|6|7|8|9)xl/, // You can display all the colors that you need
      variants: ['lg', 'hover', 'focus', 'lg:hover'],      // Optional
    },
    {
      pattern: /items-.*/,
    },
  ],
  theme: {
    extend: {
      colors: {
        dark: '#141414',
        neutral: '#faf5f5',
        primary: '#00ff00',
        secondary: '#9673ff',
        'additional-01': '#ff3719',
        'additional-02': '#66f2ff',

        'primary-tint-01': '#009900',
        'primary-tint-02': '#00be00',
        'primary-tint-03': '#00d300',
        'primary-tint-04': '#00ea00',
        'primary-tint-05': '#a3ff90',
        'primary-tint-06': '#ccffbe',
        'primary-tint-07': '#ebffe5',

        'secondary-tint-01': '#4d2eed',
        'secondary-tint-02': '#5c33f4',
        'secondary-tint-03': '#7952fe',
        'secondary-tint-04': '#b69dfe',
        'secondary-tint-05': '#d4c4fe',
        'secondary-tint-06': '#efe7ff',
        background: '#141414',
      },
      fontFamily: {
        'headline': ['KarioDuplexVar'],
        'sans': ['OfficerSans', ...defaultTheme.fontFamily.sans],
        'sans-condensed': ['OfficerSansCond'],
      },
      gridTemplateColumns: {
        'schedule': 'max-content 15px 1fr',
      }
    },
  },
  plugins: [],
}

