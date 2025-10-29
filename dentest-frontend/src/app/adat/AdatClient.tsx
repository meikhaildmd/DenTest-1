"use client";
import { useEffect } from "react";
import { useTheme } from "@/components/ThemeProvider";

export default function AdatClient() {
    const { setTheme } = useTheme();

    useEffect(() => {
        setTheme("adat");
    }, [setTheme]);

    return null;
}