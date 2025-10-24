/* src/app/adat/page.tsx */
import Link from 'next/link';
import { ArrowLeft, ClipboardList } from 'lucide-react';

interface Section { id: number; name: string; }
interface ProgressRow { subject_id: number; percent: number; }

/* helper ─ fetch user progress, map subject_id → percentage */
async function getProgress(): Promise<Record<number, number>> {
  const API = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!API) return {};

  try {
    const r = await fetch(`${API}/user-progress/`, {
      credentials: 'include',
      cache: 'no-store',
    });

    // if not logged in or forbidden → just return empty progress
    if (r.status === 403 || r.status === 401) return {};
    if (!r.ok) return {};

    const rows: ProgressRow[] = await r.json();
    return Object.fromEntries(rows.map(p => [p.subject_id, p.percent]));
  } catch {
    return {};
  }
}

export default async function AdatHome() {
  const API = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!API) return <div>Error: API base URL not set</div>;

  let sections: Section[] = [];
  let progress: Record<number, number> = {};

  try {
    const [sectionRes, progressData] = await Promise.all([
      fetch(`${API}/sections/adat/`, { cache: 'no-store' }),
      getProgress(),
    ]);

    if (sectionRes.ok) sections = await sectionRes.json();
    progress = progressData;
  } catch (err) {
    console.error("Error loading ADAT data:", err);
  }

  return (
    <div className="min-h-screen p-6">

      {/* ───────── navigation back home ───────── */}
      <Link
        href="/"
        className="inline-flex items-center gap-2 mb-6
                   text-blue-400 hover:text-blue-300 transition"
      >
        <ArrowLeft size={18} /> Home
      </Link>

      <h1 className="text-3xl font-bold mb-2">ADAT Sections</h1>
      <p className="mb-6 text-neutral-400">
        Choose a section to drill focused questions — or build a custom set.
      </p>

      {/* grid of section cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {sections.map((s: Section) => (
          <Link
            key={s.id}
            href={`/adat/section/${s.id}`}
            className="
              group relative overflow-hidden rounded-xl
              bg-blue-600/90 hover:bg-blue-600
              border-4 border-purple-400
              p-5 shadow-lg transition hover:-translate-y-1
            "
          >
            <ClipboardList
              size={28}
              className="text-white/90 mb-4 group-hover:scale-110 transition-transform"
            />

            <h2 className="text-xl font-semibold text-white">{s.name}</h2>

            {progress[s.id] !== undefined && (
              <span className="
                mt-3 inline-block rounded-full bg-white/20
                px-3 py-1 text-sm font-medium text-white/80
              ">
                {progress[s.id]} % complete
              </span>
            )}
          </Link>
        ))}
      </div>

      {/* custom-quiz entry */}
      <div className="mt-10 text-center">
        <Link
          href="/custom?exam=adat"
          className="inline-block rounded px-6 py-3 bg-blue-600
                     hover:bg-blue-700 transition text-white font-semibold"
        >
          Build a custom ADAT quiz
        </Link>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────
   Duplicate this file for ADAT:
   - Save as src/app/adat/page.tsx
   - Replace every "inbde" with "adat"
   - Adjust card colours if you wish
   ──────────────────────────────────── */