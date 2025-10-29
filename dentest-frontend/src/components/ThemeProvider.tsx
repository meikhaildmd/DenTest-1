"use client";
import React, { createContext, useContext, useEffect, useState } from "react";

type Theme = "home" | "inbde" | "adat";

interface ThemeContextType {
    theme: Theme;
    setTheme: (t: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType>({
    theme: "home",
    setTheme: () => { },
});

export const useTheme = () => useContext(ThemeContext);

const themePresets: Record<Theme, Record<string, string>> = {
    home: {
        "--theme-gradient": "linear-gradient(to right, #34d399, #10b981, #0d9488)",
        "--color-accent": "#10b981",
        "--color-accent-secondary": "#34d399",
        "--color-background": "#0a0a0a",
        "--color-foreground": "#ffffff",
    },
    inbde: {
        "--theme-gradient": "linear-gradient(to right, #3b82f6, #6366f1, #8b5cf6)",
        "--color-accent": "#6366f1",
        "--color-accent-secondary": "#3b82f6",
        "--color-background": "#0b0b17",
        "--color-foreground": "#f5f5f5",
    },
    adat: {
        "--theme-gradient": "linear-gradient(to right, #059669, #14b8a6, #06b6d4)",
        "--color-accent": "#14b8a6",
        "--color-accent-secondary": "#06b6d4",
        "--color-background": "#081412",
        "--color-foreground": "#ecfeff",
    },
};

export default function ThemeProvider({ children }: { children: React.ReactNode }) {
    const [theme, setTheme] = useState<Theme>("home");

    useEffect(() => {
        const root = document.documentElement;
        const vars = themePresets[theme];
        Object.entries(vars).forEach(([key, value]) => {
            root.style.setProperty(key, value);
        });
    }, [theme]);

    return (
        <ThemeContext.Provider value={{ theme, setTheme }}>
            {children}
        </ThemeContext.Provider>
    );
}