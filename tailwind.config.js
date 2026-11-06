/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,js}",
    "./node_modules/flowbite/**/*.js",
    "./src/**/forms.py"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#1d4ed8",
          strong: "#1e40af",
          medium: "#bfdbfe",
        },
      },
    },
  },
  plugins: [
      require('flowbite/plugin')
  ]
}
