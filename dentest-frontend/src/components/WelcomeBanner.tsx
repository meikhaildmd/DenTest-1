'use client';
import { useEffect, useState } from 'react';

/* large, centered banner – shows only when authenticated */
export default function WelcomeHeroBanner() {
    const [name, setName] = useState<string | null>(null);

    /* ask Django who we are */
    useEffect(() => {
        fetch('http://127.0.0.1:8000/api/current-user/', {
            credentials: 'include',
            cache: 'no-store',
        })
            .then(r => (r.ok ? r.json() : null))
            .then(d => setName(d?.username ?? null))
            .catch(() => { });
    }, []);

    if (!name) return null;           // guest → render nothing

    return (
        <div
            className="
        mx-auto mb-8 w-fit
        rounded-full py-3 px-6
        text-xl sm:text-2xl font-semibold
        text-white shadow-lg
        bg-gradient-to-r from-purple-500 via-blue-500 to-cyan-500
        animate-slide-down
      "
        >
            Welcome, {name}!
        </div>
    );
}