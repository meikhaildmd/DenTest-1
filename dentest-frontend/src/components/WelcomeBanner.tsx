'use client';
import { useEffect, useState } from 'react';

export default function WelcomeHeroBanner() {
    const [name, setName] = useState<string | null>(null);
    const API = process.env.NEXT_PUBLIC_API_BASE_URL;

    useEffect(() => {
        if (!API) return;
        fetch(`${API}/api/current-user/`, {
            credentials: 'include',
            cache: 'no-store',
        })
            .then(r => (r.ok ? r.json() : null))
            .then(d => setName(d?.username ?? null))
            .catch(() => { });
    }, [API]);

    if (!name) return null;

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