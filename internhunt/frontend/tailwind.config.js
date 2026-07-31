/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Primary brand palette
        brand: {
          50: "hsl(221, 100%, 96%)",
          100: "hsl(221, 100%, 90%)",
          200: "hsl(221, 90%, 80%)",
          300: "hsl(221, 85%, 68%)",
          400: "hsl(221, 82%, 58%)",
          500: "hsl(221, 80%, 50%)",   // primary
          600: "hsl(221, 80%, 42%)",
          700: "hsl(221, 80%, 34%)",
          800: "hsl(221, 80%, 26%)",
          900: "hsl(221, 80%, 18%)",
        },
        // Surface colours for dark UI
        surface: {
          50: "hsl(220, 20%, 97%)",
          100: "hsl(220, 16%, 90%)",
          200: "hsl(222, 14%, 78%)",
          600: "hsl(222, 16%, 28%)",
          700: "hsl(222, 18%, 18%)",
          800: "hsl(222, 20%, 13%)",
          850: "hsl(222, 22%, 10%)",
          900: "hsl(222, 24%, 8%)",
          950: "hsl(222, 28%, 5%)",
        },
        // Status colours
        success: "hsl(142, 72%, 42%)",
        warning: "hsl(38, 92%, 50%)",
        danger: "hsl(0, 78%, 58%)",
        info: "hsl(199, 89%, 48%)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      backgroundImage: {
        "gradient-brand":
          "linear-gradient(135deg, hsl(221,80%,50%), hsl(260,70%,55%))",
        "gradient-dark":
          "linear-gradient(180deg, hsl(222,24%,8%) 0%, hsl(222,20%,13%) 100%)",
        "glass":
          "linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02))",
      },
      boxShadow: {
        "glow-brand": "0 0 20px hsl(221,80%,50%,0.3)",
        "glow-success": "0 0 20px hsl(142,72%,42%,0.3)",
        glass: "inset 0 1px 0 rgba(255,255,255,0.08), 0 4px 24px rgba(0,0,0,0.4)",
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.3s ease-out",
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        shimmer: "shimmer 2s linear infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
    },
  },
  plugins: [],
};
