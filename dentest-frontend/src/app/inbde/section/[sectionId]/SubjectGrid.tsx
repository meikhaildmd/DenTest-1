'use client';
export const dynamic = "force-dynamic";
import { useEffect, useState } from 'react';
import Link from 'next/link';

/* ---------- types ---------- */
interface Subject {
    id: number;
    name: string;
}
interface ProgressRow {
    subject_id: number;
    correct: number;
    total: number;
}
interface Props {
    subjects: Subject[];
}

/* ---------- component ---------- */
export default function SubjectGrid({ subjects }: Props) {
    const [pct, setPct] = useState<Record<number, number>>({});
    const API = process.env.NEXT_PUBLIC_API_BASE_URL; // ✅ use env for backend URL

    /* ---------- load user progress ---------- */
    useEffect(() => {
        if (!API) return;
        fetch(`${API}/user-progress/`, {
            credentials: 'include',
            cache: 'no-store',
        })
            .then((r) => (r.status === 403 ? [] : r.json()))
            .then((rows: ProgressRow[]) => {
                const m: Record<number, number> = {};
                rows.forEach((p) => {
                    m[p.subject_id] = p.total
                        ? Math.round((p.correct / p.total) * 100)
                        : 0;
                });
                setPct(m);
            })
            .catch(() => { /* ignore network errors */ });
    }, [API]);

    /* ---------- helpers ---------- */
    const pctColor = (p: number) =>
        p >= 80 ? 'text-green-400'
            : p >= 50 ? 'text-yellow-400'
                : 'text-red-400';

    const ringColor = (p: number) =>
        p >= 80 ? '#22c55e'      // green
            : p >= 50 ? '#facc15'    // yellow
                : '#ef4444';             // red

    /* ---------- render ---------- */
    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {subjects.map((s) => {
                const p = pct[s.id];
                const deg = (p ?? 0) * 3.6;
                const ring = ringColor(p ?? 0);

                return (
                    <Link
                        key={s.id}
                        href={`/inbde/quiz/${s.id}`}
                        className="
              group relative rounded-xl p-5 bg-neutral-800
              hover:-translate-y-1 hover:shadow-lg transition
            "
                    >
                        {/* Subject name */}
                        <h2 className="font-semibold text-white mb-4">{s.name}</h2>

                        {/* Progress ring + percentage */}
                        {p !== undefined ? (
                            <div className="flex items-center gap-4">
                                <div
                                    className="relative w-12 h-12 rounded-full shrink-0"
                                    style={{
                                        background: `conic-gradient(${ring} ${deg}deg, #334155 ${deg}deg)`,
                                    }}
                                >
                                    <div className="absolute inset-1 rounded-full bg-neutral-900" />
                                </div>

                                <span className={`text-xl font-medium ${pctColor(p)}`}>
                                    {p} %
                                </span>
                            </div>
                        ) : (
                            <span className="text-sm text-neutral-400">Not started</span>
                        )}
                    </Link>
                );
            })}
        </div>
    );
}