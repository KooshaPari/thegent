/**
 * Design Tokens for BytePort
 * Centralized design system values for consistent styling
 */

export const designTokens = {
  // Color Palette
  colors: {
    // Primary colors
    primary: {
      50: 'hsl(217, 91%, 95%)',
      100: 'hsl(217, 91%, 90%)',
      200: 'hsl(217, 91%, 80%)',
      300: 'hsl(217, 91%, 70%)',
      400: 'hsl(217, 91%, 65%)',
      500: 'hsl(217, 91%, 59.8%)', // Default
      600: 'hsl(217, 91%, 50%)',
      700: 'hsl(217, 91%, 40%)',
      800: 'hsl(217, 91%, 30%)',
      900: 'hsl(217, 91%, 20%)',
    },

    // Semantic colors
    success: {
      light: 'hsl(142, 76%, 36%)',
      DEFAULT: 'hsl(142, 76%, 36%)',
      dark: 'hsl(142, 76%, 30%)',
    },
    warning: {
      light: 'hsl(38, 92%, 50%)',
      DEFAULT: 'hsl(38, 92%, 45%)',
      dark: 'hsl(38, 92%, 40%)',
    },
    error: {
      light: 'hsl(0, 84%, 60%)',
      DEFAULT: 'hsl(0, 72%, 51%)',
      dark: 'hsl(0, 65%, 45%)',
    },
    info: {
      light: 'hsl(199, 89%, 48%)',
      DEFAULT: 'hsl(199, 89%, 42%)',
      dark: 'hsl(199, 89%, 36%)',
    },

    // Neutral colors
    neutral: {
      50: 'hsl(210, 40%, 98%)',
      100: 'hsl(210, 40%, 96%)',
      200: 'hsl(214, 32%, 91%)',
      300: 'hsl(213, 27%, 84%)',
      400: 'hsl(215, 20%, 65%)',
      500: 'hsl(215, 16%, 47%)',
      600: 'hsl(215, 19%, 35%)',
      700: 'hsl(215, 25%, 27%)',
      800: 'hsl(217, 33%, 17%)',
      900: 'hsl(222, 47%, 11%)',
    },
  },

  // Spacing Scale (based on 4px grid)
  spacing: {
    0: '0',
    1: '0.25rem',    // 4px
    2: '0.5rem',     // 8px
    3: '0.75rem',    // 12px
    4: '1rem',       // 16px
    5: '1.25rem',    // 20px
    6: '1.5rem',     // 24px
    8: '2rem',       // 32px
    10: '2.5rem',    // 40px
    12: '3rem',      // 48px
    16: '4rem',      // 64px
    20: '5rem',      // 80px
    24: '6rem',      // 96px
    32: '8rem',      // 128px
  },

  // Typography Scale
  typography: {
    fontSize: {
      xs: '0.75rem',      // 12px
      sm: '0.875rem',     // 14px
      base: '1rem',       // 16px
      lg: '1.125rem',     // 18px
      xl: '1.25rem',      // 20px
      '2xl': '1.5rem',    // 24px
      '3xl': '1.875rem',  // 30px
      '4xl': '2.25rem',   // 36px
      '5xl': '3rem',      // 48px
      '6xl': '3.75rem',   // 60px
      '7xl': '4.5rem',    // 72px
    },
    fontWeight: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800,
    },
    lineHeight: {
      none: 1,
      tight: 1.25,
      snug: 1.375,
      normal: 1.5,
      relaxed: 1.625,
      loose: 2,
    },
    letterSpacing: {
      tighter: '-0.05em',
      tight: '-0.025em',
      normal: '0',
      wide: '0.025em',
      wider: '0.05em',
      widest: '0.1em',
    },
  },

  // Border Radius
  borderRadius: {
    none: '0',
    sm: 'calc(var(--radius) - 4px)',
    md: 'calc(var(--radius) - 2px)',
    lg: 'var(--radius)',              // 0.5rem / 8px
    xl: 'calc(var(--radius) + 4px)',
    '2xl': 'calc(var(--radius) + 8px)',
    full: '9999px',
  },

  // Shadows
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
    none: 'none',
  },

  // Transitions
  transitions: {
    duration: {
      fast: '150ms',
      base: '200ms',
      medium: '300ms',
      slow: '500ms',
    },
    timing: {
      linear: 'linear',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      spring: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    },
  },

  // Z-Index Scale
  zIndex: {
    0: 0,
    10: 10,
    20: 20,
    30: 30,
    40: 40,
    50: 50,
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    modalBackdrop: 1040,
    modal: 1050,
    popover: 1060,
    tooltip: 1070,
  },

  // Breakpoints
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },

  // Container Max Widths
  container: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1400px',
  },
} as const;

// Type helper for accessing design tokens
export type DesignTokens = typeof designTokens;
