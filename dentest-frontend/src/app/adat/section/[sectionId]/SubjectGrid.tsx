/* src/app/inbde/section/[sectionId]/SubjectGrid.tsx
   client component – coloured progress rings + sectionId in URL */
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

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
    sectionId: string;          // ← add this prop
}

export default function SubjectGrid({ subjects, sectionId }: Props) {
    const [pct, setPct] = useState<Record<number, number>>({});

    /* load user progress once */
    useEffect(() => {
        fetch('http://127.0.0.1:8000/api/user-progress/', {
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
            });
    }, []);

    /* helpers */
    const pctColor = (p: number) =>
        p >= 80 ? 'text-green-400'
            : p >= 50 ? 'text-yellow-400'
                : 'text-red-400';

    const ringColor = (p: number) =>
        p >= 80 ? '#22c55e'      // green-500
            : p >= 50 ? '#facc15'    // yellow-400
                : '#ef4444';             // red-500

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {subjects.map((s) => {
                const p = pct[s.id];                         // undefined if never attempted
                const deg = (p ?? 0) * 3.6;
                const ring = ringColor(p ?? 0);

                return (
                    <Link
                        key={s.id}
                        href={`/adat/quiz/${s.id}?sectionId=${sectionId}`}  /* ← section in query */
                        className="
              group relative rounded-xl p-5 bg-neutral-800
              hover:-translate-y-1 hover:shadow-lg transition
            "
                    >
                        {/* title */}
                        <h2 className="font-semibold text-white mb-4">{s.name}</h2>

                        {/* progress ring + number */}
                        {p !== undefined ? (
                            <div className="flex items-center gap-4">
                                {/* ring */}
                                <div
                                    className="relative w-12 h-12 rounded-full shrink-0"
                                    style={{
                                        background: `conic-gradient(${ring} ${deg}deg, #334155 ${deg}deg)`,
                                    }}
                                >
                                    <div className="absolute inset-1 rounded-full bg-neutral-900" />
                                </div>

                                {/* number */}
                                <span className={`text-xl font-medium ${pctColor(p)}`}>
                                    {p} %
                                </span>
                            </div>
                        ) : (
                            <span className="text-sm text-neutral-400">
                                Not started
                            </span>
                        )}
                    </Link>
                );
            })}
        </div>
    );
}