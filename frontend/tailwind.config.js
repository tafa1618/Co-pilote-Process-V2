/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        onyx: "#000000",
        "cat-yellow": "#FFCD11", // Official-ish Caterpillar Yellow
        gold: "#FFD700", // Plan approved backup
        sand: "#F2E8DA",
      },
      fontFamily: {
        display: ["'Inter'", "system-ui", "sans-serif"],
      },
      boxShadow: {
        luxe: "0 20px 60px -25px rgba(198, 161, 91, 0.35)",
      },
    },
  },
  plugins: [],
};
