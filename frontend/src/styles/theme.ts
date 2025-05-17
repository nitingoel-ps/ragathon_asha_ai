const theme = {
    // Colors
    colors: {
        primary: '#6200ee',
        secondary: '#03dac6',
        error: '#b00020',
        background: '#ffffff',
        surface: '#f5f5f5',
        text: {
            primary: '#333333',
            secondary: '#757575',
            disabled: '#9e9e9e',
            hint: '#9e9e9e',
        },
    },

    // Typography
    typography: {
        fontFamily: {
            primary: '"Roboto", "Helvetica", "Arial", sans-serif',
            secondary: '"Playfair Display", serif',
        },
        fontSize: {
            xs: '0.75rem',    // 12px
            sm: '0.875rem',   // 14px
            base: '1rem',     // 16px
            lg: '1.125rem',   // 18px
            xl: '1.25rem',    // 20px
            '2xl': '1.5rem',  // 24px
            '3xl': '1.875rem',// 30px
            '4xl': '2.25rem', // 36px
            '5xl': '3rem',    // 48px
        },
        fontWeight: {
            light: 300,
            regular: 400,
            medium: 500,
            bold: 700,
        },
        lineHeight: {
            tight: 1.25,
            base: 1.5,
            relaxed: 1.75,
        },
    },

    // Spacing
    spacing: {
        xs: '0.25rem',   // 4px
        sm: '0.5rem',    // 8px
        md: '1rem',      // 16px
        lg: '1.5rem',    // 24px
        xl: '2rem',      // 32px
        '2xl': '2.5rem', // 40px
        '3xl': '3rem',   // 48px
    },

    // Breakpoints
    breakpoints: {
        xs: '320px',
        sm: '576px',
        md: '768px',
        lg: '992px',
        xl: '1200px',
    },

    // Border radius
    borderRadius: {
        sm: '0.125rem',  // 2px
        md: '0.25rem',   // 4px
        lg: '0.5rem',    // 8px
        full: '9999px',  // circle
    },

    // Shadows
    shadows: {
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    },

    // z-index
    zIndex: {
        hide: -1,
        base: 0,
        dropdown: 1000,
        sticky: 1100,
        modal: 1300,
        tooltip: 1400,
    },

    // Transitions
    transitions: {
        fast: '150ms',
        normal: '300ms',
        slow: '500ms',
    }
};

export default theme;