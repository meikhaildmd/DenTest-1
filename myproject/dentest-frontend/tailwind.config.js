/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: 'class',            // ✨ allow manual toggle
    content: [

        './src/**/*.{js,ts,jsx,tsx,mdx}',   // <-- MUST include the app directory
        './src/app/**/*.{js,ts,jsx,tsx}',
    ],
    theme: { extend: {} },
    plugins: [],
};