'use client';
export const dynamic = "force-dynamic";
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const handleLogin = async () => {
        setError(null);

        try {
            // 1 ─ fetch CSRF cookie + token
            const csrfRes = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/csrf/`, {
                credentials: 'include',
            });
            const { csrftoken } = await csrfRes.json();
            if (!csrftoken) throw new Error('CSRF token missing');

            // 2 ─ POST credentials
            const r = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                credentials: 'include',
                body: JSON.stringify({ username, password }),
            });

            if (!r.ok) throw new Error('Invalid username or password');

            // 3 ─ success → go home
            router.push('/');
        } catch (err: unknown) {
            if (err instanceof Error) {
                setError(err.message || 'Login error');
                console.error(err);
            } else {
                setError('Login error');
            }
        }
    };

    const handleGuest = () => {
        // No login request → just go home as guest
        router.push('/');
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-8">
            <div className="w-full max-w-sm bg-neutral-900 rounded-lg p-6 shadow">
                <h1 className="text-2xl font-bold mb-6 text-center">Log&nbsp;in</h1>

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
                        className="w-full bg-blue-600 hover:bg-blue-700 transition text-white font-semibold py-2 rounded"
                    >
                        Log&nbsp;in
                    </button>

                    <button
                        onClick={handleGuest}
                        className="w-full bg-neutral-700 hover:bg-neutral-600 transition text-white font-medium py-2 rounded"
                    >
                        Continue as Guest
                    </button>
                </div>
            </div>
        </div>
    );
}