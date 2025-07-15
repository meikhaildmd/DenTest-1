/* src/app/login/page.tsx */
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    /* helper ─ read cookie */
    function getCookie(name: string) {
        const m = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return m ? decodeURIComponent(m[2]) : null;
    }

    const handleLogin = async () => {
        setError(null);

        try {
            /* 1 ─ fetch CSRF cookie */
            await fetch('http://127.0.0.1:8000/api/csrf/', {
                credentials: 'include',
            });

            const csrf = getCookie('csrftoken');
            if (!csrf) throw new Error('CSRF token missing');

            /* 2 ─ POST credentials */
            const r = await fetch('http://127.0.0.1:8000/api/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf,
                },
                credentials: 'include',
                body: JSON.stringify({ username, password }),
            });

            if (!r.ok) throw new Error('Invalid username or password');

            /* 3 ─ success → go home */
            router.push('/');
        } catch (err: any) {
            setError(err.message || 'Login error');
            console.error(err);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-8">
            <div className="w-full max-w-sm bg-neutral-900 rounded-lg p-6 shadow">
                <h1 className="text-2xl font-bold mb-6 text-center">Log&nbsp;in</h1>

                <input
                    type="text"
                    placeholder="Username"
                    className="block w-full border p-2 mb-3 rounded
                     bg-neutral-800 text-white placeholder-gray-400"
                    value={username}
                    onChange={e => setUsername(e.target.value)}
                />

                <input
                    type="password"
                    placeholder="Password"
                    className="block w-full border p-2 mb-4 rounded
                     bg-neutral-800 text-white placeholder-gray-400"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                />

                {error && (
                    <p className="mb-4 text-sm text-red-400 text-center">{error}</p>
                )}

                <button
                    onClick={handleLogin}
                    className="w-full bg-blue-600 hover:bg-blue-700 transition
                     text-white font-semibold py-2 rounded"
                >
                    Log&nbsp;in
                </button>
            </div>
        </div>
    );
}