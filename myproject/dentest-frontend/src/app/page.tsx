/* src/app/page.tsx */
import Link from 'next/link';
import WelcomeBanner from '@/components/WelcomeBanner';   // ⬅️ new big banner

export default function Home() {
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

        {/* Log-in */}
        <Link
          href="/login"
          className="px-4 py-2 rounded bg-neutral-800 hover:bg-neutral-700 transition text-white font-medium"
        >
          Log&nbsp;in
        </Link>
      </nav>

      {/* ───────── hero ───────── */}
      <div className="text-center max-w-xl">

        {/* colourful greeting – rendered only when authenticated */}
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