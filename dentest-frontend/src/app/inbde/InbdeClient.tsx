"use client";
import { useEffect } from "react";
import { useTheme } from "@/components/ThemeProvider";

export default function InbdeClient() {
    const { setTheme } = useTheme();

    useEffect(() => {
        setTheme("inbde");
    }, [setTheme]);

    return null;
}