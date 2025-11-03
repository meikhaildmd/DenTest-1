'use client';
export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
    const router = useRouter();

    // ── form + feedback state ────────────────────────────────
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [checkingSession, setCheckingSession] = useState(true);

    // ── check existing session on mount ──────────────────────
    useEffect(() => {
        (async () => {
            try {
                const res = await fetch(
                    `${process.env.NEXT_PUBLIC_API_BASE_URL}/current-user/`,
                    { credentials: 'include' }
                );
                if (res.ok) {
                    // already logged in → go home
                    router.push('/');
                    return;
                }
            } catch {
                // ignore, just continue to login form
            } finally {
                setCheckingSession(false);
            }
        })();
    }, [router]);

    // ── handle login submission ──────────────────────────────
    const handleLogin = async () => {
        setError(null);
        setLoading(true);

        try {
            // 1️⃣ get CSRF token
            const csrfRes = await fetch(
                `${process.env.NEXT_PUBLIC_API_BASE_URL}/csrf/`,
                { credentials: 'include' }
            );
            const { csrftoken } = await csrfRes.json();
            if (!csrftoken) throw new Error('CSRF token missing');

            // 2️⃣ send credentials
            const r = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                credentials: 'include',
                body: JSON.stringify({ username, password }),
            });

            if (!r.ok) throw new Error('Invalid username or password');

            // 3️⃣ success → home
            router.push('/');
        } catch (err: unknown) {
            if (err instanceof Error) {
                setError(err.message || 'Login error');
            } else {
                setError('Login error');
            }
        } finally {
            setLoading(false);
        }
    };

    // ── continue as guest ────────────────────────────────────
    const handleGuest = () => router.push('/');

    // ── show “checking session” while verifying ──────────────
    if (checkingSession) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <p className="text-neutral-400 animate-pulse text-lg">
                    Checking session…
                </p>
            </div>
        );
    }

    // ── main render ──────────────────────────────────────────
    return (
        <div className="min-h-screen flex items-center justify-center p-8">
            <div className="w-full max-w-sm bg-neutral-900 rounded-lg p-6 shadow">
                <h1 className="text-2xl font-bold mb-6 text-center text-white">
                    Log&nbsp;in
                </h1>

                <input
                    type="text"
                    placeholder="Username"
                    className="block w-full border p-2 mb-3 rounded bg-neutral-800 text-white placeholder-gray-400"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />

                <input
                    type="password"
                    placeholder="Password"
                    className="block w-full border p-2 mb-4 rounded bg-neutral-800 text-white placeholder-gray-400"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />

                {error && (
                    <p className="mb-4 text-sm text-red-400 text-center">{error}</p>
                )}

                <div className="flex flex-col gap-3">
                    <button
                        onClick={handleLogin}
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-700 transition text-white font-semibold py-2 rounded disabled:opacity-60"
                    >
                        {loading ? 'Logging in…' : 'Log in'}
                    </button>

                    <button
                        onClick={handleGuest}
                        className="w-full bg-neutral-700 hover:bg-neutral-600 transition text-white font-medium py-2 rounded"
                    >
                        Continue as Guest
                    </button>
                </div>

                <p className="text-center text-sm mt-4 text-gray-400">
                    Don’t have an account?{' '}
                    <a href="/signup" className="text-purple-400 hover:underline">
                        Sign up
                    </a>
                </p>
            </div>
        </div>
    );
}