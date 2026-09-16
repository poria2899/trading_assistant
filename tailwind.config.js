/**
 * Tailwind config for the Trade Assistant UI/UX redesign.
 *
 * Centralizes the design tokens (colors, radius, shadows, durations)
 * referenced in the design brief so templates use tailwind utilities /
 * theme() values instead of scattered hex codes.
 */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./apps/**/templates/**/*.html",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: "#0b0d10",
        surface: {
          DEFAULT: "#14171c",
          raised: "#1a1e24",
        },
        border: {
          DEFAULT: "#242830",
          subtle: "#1c2027",
        },
        text: {
          DEFAULT: "#f2f3f5",
          muted: "#9aa0ab",
          faint: "#6b7280",
        },
        primary: {
          DEFAULT: "#e5484d",
          hover: "#ef5f63",
          active: "#c93c40",
          muted: "#3a1f21",
        },
        success: {
          DEFAULT: "#22c55e",
          muted: "#123321",
        },
        danger: {
          DEFAULT: "#e5484d",
          muted: "#3a1f21",
        },
        warning: {
          DEFAULT: "#eab308",
          muted: "#332b12",
        },
        neutral: {
          DEFAULT: "#8b93a1",
          muted: "#20242c",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "Arial",
          "sans-serif",
        ],
      },
      borderRadius: {
        sm: "6px",
        DEFAULT: "8px",
        lg: "12px",
        xl: "16px",
      },
      boxShadow: {
        card: "0 1px 2px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.02)",
        elevated: "0 8px 24px rgba(0,0,0,0.45)",
      },
      transitionDuration: {
        DEFAULT: "160ms",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "toast-in": {
          "0%": { opacity: "0", transform: "translateY(-8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in": "fade-in 240ms ease-out both",
        "fade-in-up": "fade-in-up 320ms ease-out both",
        "toast-in": "toast-in 200ms ease-out both",
      },
    },
  },
  plugins: [],
};
