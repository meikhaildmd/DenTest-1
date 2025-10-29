/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: 'class',            // ✨ allow manual toggle
    content: [

        './src/**/*.{js,ts,jsx,tsx,mdx}',   // <-- MUST include the app directory
        './src/app/**/*.{js,ts,jsx,tsx}',
    ],
    theme: {
        extend: {
            backgroundImage: {
                'theme-gradient': 'var(--theme-gradient)',
            },
            colors: {
                accent: 'var(--color-accent)',
                'accent-secondary': 'var(--color-accent-secondary)',
                background: 'var(--color-background)',
                foreground: 'var(--color-foreground)',
            },
        },
    },
    plugins: [],
};