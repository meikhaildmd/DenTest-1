'use client';
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export default function WelcomeBanner() {
    const [name, setName] = useState<string | null>(null);
    const API = process.env.NEXT_PUBLIC_API_BASE_URL;

    useEffect(() => {
        if (!API) return;
        fetch(`${API}/api/current-user/`, {
            credentials: 'include',
            cache: 'no-store',
        })
            .then((r) => (r.ok ? r.json() : null))
            .then((d) => setName(d?.username ?? null))
            .catch(() => { });
    }, [API]);

    if (!name) return null;

    return (
        <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className="mx-auto mb-10 w-fit rounded-full py-4 px-8 text-2xl sm:text-3xl
                 font-extrabold tracking-tight border border-white/10 backdrop-blur-md
                 shimmer-text"
        >
            Welcome, {name}!
        </motion.div>
    );
}