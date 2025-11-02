'use client';

import Link from 'next/link';
import WelcomeBanner from '@/components/WelcomeBanner';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { apiLogout } from '@/lib/auth';

interface User {
  username: string;
}

export default function Home() {
  const [name, setName] = useState<string | null>(null);
  const router = useRouter();
  const API = process.env.NEXT_PUBLIC_API_BASE_URL;

  // --- Load current user on mount ---
  useEffect(() => {
    if (!API) return;
    fetch(`${API}/current-user/`, {
      credentials: 'include',
      cache: 'no-store',
    })
      .then((r) => (r.ok ? r.json() : null))
      .then((d: User | null) => setName(d?.username ?? null))
      .catch(() => setName(null));
  }, [API]);

  // --- Handle logout ---
  const handleLogout = async () => {
    try {
      await apiLogout();          // actually logs out on backend
    } catch (e) {
      console.error(e);
    } finally {
      setName(null);
      router.replace('/login?loggedout=1');  // navigates after logout
      router.refresh();                     // forces re-check of current-user
    }
  };
  return (
    <main className="relative min-h-screen flex flex-col items-center justify-center text-white overflow-hidden">
      {/* 🌈 Animated INBDE↔ADAT background */}
      <div className="absolute inset-0 animate-multi-gradient opacity-95" />
      {/* soft radial grain overlay */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(255,255,255,0.06)_0%,transparent_70%)] mix-blend-overlay pointer-events-none" />

      {/* ───────── NAV ───────── */}
      <nav className="absolute top-0 left-0 w-full p-4 flex items-center gap-4 z-10">
        <Link
          href="/inbde"
          className="px-4 py-2 rounded-full font-medium
                     bg-gradient-to-r from-blue-600 via-purple-600 to-fuchsia-500
                     hover:brightness-110 transition shadow-md"
        >
          INBDE
        </Link>
        <Link
          href="/adat"
          className="px-4 py-2 rounded-full font-medium
                     bg-gradient-to-r from-emerald-700 via-teal-600 to-emerald-400
                     hover:brightness-110 transition shadow-md"
        >
          ADAT
        </Link>

        {/* Right side auth */}
        <div className="ml-auto">
          {name ? (
            <button
              onClick={handleLogout}
              className="px-4 py-2 rounded-full bg-neutral-900/60 hover:bg-neutral-800/70
                         backdrop-blur-md transition text-white font-medium border border-white/10 shadow-md"
            >
              Log out
            </button>
          ) : (
            <Link
              href="/login"
              className="px-4 py-2 rounded-full bg-neutral-900/60 hover:bg-neutral-800/70
                         backdrop-blur-md transition text-white font-medium border border-white/10 shadow-md"
            >
              Log in
            </Link>
          )}
        </div>
      </nav>

      {/* ───────── HERO ───────── */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.9, ease: 'easeOut' }}
        className="text-center max-w-2xl z-10 px-4"
      >
        <WelcomeBanner />

        {/* shimmering title */}
        <h1 className="text-4xl sm:text-5xl font-extrabold mb-4 bg-animated-text bg-clip-text text-transparent drop-shadow-[0_0_20px_rgba(0,180,255,0.3)]">
          Ace Your Dental Boards with ToothPrep
        </h1>

        <p className="text-lg mb-8 text-neutral-300 leading-relaxed">
          Focused questions, clear explanations, and progress tracking — everything you need to succeed.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Link
            href="/inbde"
            className="rounded-full px-8 py-3 font-semibold text-white shadow-lg
                       bg-gradient-to-r from-blue-500 via-purple-500 to-fuchsia-500
                       hover:scale-105 active:scale-95 transition-transform"
          >
            Start INBDE Practice
          </Link>
          <Link
            href="/adat"
            className="rounded-full px-8 py-3 font-semibold text-white shadow-lg
                       bg-gradient-to-r from-emerald-700 via-teal-600 to-emerald-400
                       hover:scale-105 active:scale-95 transition-transform"
          >
            Start ADAT Practice
          </Link>
        </div>
      </motion.div>
    </main>
  );
}