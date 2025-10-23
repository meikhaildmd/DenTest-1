/* src/app/page.tsx */
'use client';

import Link from 'next/link';
import WelcomeBanner from '@/components/WelcomeBanner';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [name, setName] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/current-user/', {
      credentials: 'include',
      cache: 'no-store',
    })
      .then(r => (r.ok ? r.json() : null))
      .then(d => setName(d?.username ?? null))
      .catch(() => setName(null));
  }, []);

  const handleLogout = async () => {
    await fetch('http://127.0.0.1:8000/api/logout/', {
      method: 'POST',
      credentials: 'include',
    });
    setName(null);
    router.push('/login');
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-black text-white">
      {/* ───────── top-nav ───────── */}
      <nav className="absolute top-0 left-0 w-full p-4 flex items-center gap-4">
        {/* INBDE / ADAT */}
        <Link
          href="/inbde"
          className="px-4 py-2 rounded text-blue-400 hover:bg-blue-900/30 transition"
        >
          INBDE
        </Link>
        <Link
          href="/adat"
          className="px-4 py-2 rounded text-purple-400 hover:bg-purple-900/30 transition"
        >
          ADAT
        </Link>

        {/* Right side auth button */}
        <div className="ml-auto">
          {name ? (
            <button
              onClick={handleLogout}
              className="px-4 py-2 rounded bg-neutral-800 hover:bg-neutral-700 transition text-white font-medium"
            >
              Log out
            </button>
          ) : (
            <Link
              href="/login"
              className="px-4 py-2 rounded bg-neutral-800 hover:bg-neutral-700 transition text-white font-medium"
            >
              Log in
            </Link>
          )}
        </div>
      </nav>

      {/* ───────── hero ───────── */}
      <div className="text-center max-w-xl">
        <WelcomeBanner />

        <h1 className="text-4xl sm:text-5xl font-extrabold mb-4">
          Ace Your Dental Boards&nbsp;with&nbsp;DenTest
        </h1>

        <p className="text-lg mb-8 text-neutral-300">
          Targeted practice questions, instant feedback, and progress tracking for
          both INBDE and ADAT — all in one place.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Link
            href="/inbde"
            className="rounded px-6 py-3 font-semibold bg-blue-600 hover:bg-blue-700 shadow"
          >
            Start INBDE Practice
          </Link>
          <Link
            href="/adat"
            className="rounded px-6 py-3 font-semibold bg-purple-600 hover:bg-purple-700 shadow"
          >
            Start ADAT Practice
          </Link>
        </div>
      </div>
    </main>
  );
}