/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ctf: {
          bg: "#0B0F1A",
          surface: "#121829",
          border: "#1E2740",
          cyan: "#22D3EE",
          cyanHover: "#06B6D4",
          text: "#F8FAFC",
          muted: "#94A3B8"
        },
        status: {
          discovered: "#94A3B8",
          candidate: "#38BDF8",
          evidence: "#14B8A6",
          pending: "#F59E0B",
          verified: "#10B981",
          rejected: "#EF4444",
          unresolved: "#A855F7"
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        mono: ["JetBrains Mono", "Courier New", "monospace"],
      },
      borderRadius: {
        card: "12px",
      }
    },
  },
  plugins: [],
}
