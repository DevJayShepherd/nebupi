/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "../**/templates/**/*.html",
    "../**/templates/*.html",
    'node_modules/preline/dist/*.js',
  ],
  plugins: [
    require('@tailwindcss/typography'),
    require("daisyui"),
    require('preline/plugin'),
  ],
  daisyui: {
    themes: [
      "winter",
      "dark",
      {
        custom: {
          "primary": "#0072ff",
          "secondary": "#00a800",
          "accent": "#004cff",
          "neutral": "#07150b",
          "base-100": "#252933",
          "info": "#00ffff",
          "success": "#00b967",
          "warning": "#e89000",
          "error": "#ff7a7e",
        }
      },
      "cupcake",
      "bumblebee",
      "emerald",
      "corporate",
      "synthwave",
      "retro",
      "cyberpunk",
      "valentine",
      "halloween",
      "garden",
      "forest",
      "aqua",
      "lofi",
      "pastel",
      "fantasy",
      "wireframe",
      "black",
      "luxury",
      "dracula",
      "cmyk",
      "autumn",
      "business",
      "acid",
      "lemonade",
      "night",
      "coffee",
      "light",
      "dim",
      "nord",
      "sunset",
    ],
  },
}

