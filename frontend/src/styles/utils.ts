// src/styles/utils.js
export const media = {
  xs: (styles) => `@media (min-width: ${theme.breakpoints.xs}) { ${styles} }`,
  sm: (styles) => `@media (min-width: ${theme.breakpoints.sm}) { ${styles} }`,
  md: (styles) => `@media (min-width: ${theme.breakpoints.md}) { ${styles} }`,
  lg: (styles) => `@media (min-width: ${theme.breakpoints.lg}) { ${styles} }`,
  xl: (styles) => `@media (min-width: ${theme.breakpoints.xl}) { ${styles} }`,
};

// Helper to get values from theme using dot notation
export const getThemeValue =
  (path, fallback = null) =>
  (props) => {
    const pathArr = path.split('.');
    let value = props.theme;

    for (const prop of pathArr) {
      if (value[prop] === undefined) return fallback;
      value = value[prop];
    }

    return value;
  };
