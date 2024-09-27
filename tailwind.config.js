/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*",
    './static/**/*.css'
  ],
  theme: {
    extend: {
      fontFamily: {
        poppins: ['Poppins', 'sans-serif'],
      },
    },
  },
  plugins: [],
}