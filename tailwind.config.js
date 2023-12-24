/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        results: "#051247",
      },
      screens: {
        landscape: {
          raw: "(orientation: landscape) and (hover: none) and (pointer: coarse)",
        },
      },
      keyframes: {
        alert: {
          "0%": { transform: "translateY(-20px)" },
          "100%": { transform: "translateY(0px)" },
        },
        warp: {
          "0%": { translate: "-50% 100cqmax;" },
          "100%": { translate: "-50% -100%;" },
        },
      },
      animation: {
        alert: "alert 0.25s ease-out",
        warp: "warp 1s linear",
      },
    },
  },
  plugins: [require("@tailwindcss/forms"), require("tailwindcss-touch")()],
};
