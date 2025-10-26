'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function SignupPage() {
    const router = useRouter();
    const API = process.env.NEXT_PUBLIC_API_BASE_URL;

    const [form, setForm] = useState({
        username: '',
        email: '',
        password: '',
        confirm_password: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        if (form.password !== form.confirm_password) {
            setError("Passwords don't match.");
            setLoading(false);
            return;
        }

        try {
            const res = await fetch(`${API}/api/signup/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: form.username,
                    email: form.email,
                    password: form.password,
                }),
            });

            if (res.ok) {
                router.push('/login');
            } else {
                const data = await res.json();
                setError(data?.error || 'Signup failed. Please try again.');
            }
        } catch {
            setError('Network error. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="min-h-screen flex items-center justify-center bg-black text-white">
            <form
                onSubmit={handleSubmit}
                className="bg-neutral-900 p-8 rounded-2xl shadow-lg w-full max-w-md space-y-6"
            >
                <h1 className="text-3xl font-bold text-center">Create an Account</h1>

                {error && <p className="text-red-400 text-center">{error}</p>}

                <input
                    type="text"
                    name="username"
                    placeholder="Username"
                    value={form.username}
                    onChange={handleChange}
                    className="w-full p-3 rounded bg-neutral-800 text-white outline-none focus:ring-2 focus:ring-purple-600"
                    required
                />

                <input
                    type="email"
                    name="email"
                    placeholder="Email"
                    value={form.email}
                    onChange={handleChange}
                    className="w-full p-3 rounded bg-neutral-800 text-white outline-none focus:ring-2 focus:ring-purple-600"
                    required
                />

                <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    value={form.password}
                    onChange={handleChange}
                    className="w-full p-3 rounded bg-neutral-800 text-white outline-none focus:ring-2 focus:ring-purple-600"
                    required
                />

                <input
                    type="password"
                    name="confirm_password"
                    placeholder="Confirm Password"
                    value={form.confirm_password}
                    onChange={handleChange}
                    className="w-full p-3 rounded bg-neutral-800 text-white outline-none focus:ring-2 focus:ring-purple-600"
                    required
                />

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full p-3 rounded bg-purple-600 hover:bg-purple-700 transition font-semibold"
                >
                    {loading ? 'Creating Account...' : 'Sign Up'}
                </button>

                <p className="text-center text-neutral-400">
                    Already have an account?{' '}
                    <a href="/login" className="text-purple-400 hover:underline">
                        Log in
                    </a>
                </p>
            </form>
        </main>
    );
}