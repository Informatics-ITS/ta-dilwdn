/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        primary: '#AA60C8',
        secondary: '#D69ADE',
        hover: '#AF33E1',
        columntable: '#F8E3ED'
      },
      fontFamily: {
        roboto: ['Roboto', 'sans-serif'],
        aclonica: ['Aclonica', 'sans-serif']
      },
      backgroundImage: {
        registrasi: "url('/registrasi.png')"
      }
    }
  },
  plugins: []
}
