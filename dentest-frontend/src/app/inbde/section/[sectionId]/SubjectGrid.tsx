'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';

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
    const API = process.env.NEXT_PUBLIC_API_BASE_URL;

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
        p >= 80 ? 'text-indigo-400'
            : p >= 50 ? 'text-blue-300'
                : 'text-rose-400';

    const ringColor = (p: number) =>
        p >= 80 ? '#6366f1' // indigo
            : p >= 50 ? '#3b82f6' // blue
                : '#ef4444'; // red

    /* ---------- render ---------- */
    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {subjects.map((s) => {
                const p = pct[s.id];
                const deg = (p ?? 0) * 3.6;
                const ring = ringColor(p ?? 0);

                return (
                    <motion.div
                        key={s.id}
                        whileHover={{ scale: 1.03 }}
                        whileTap={{ scale: 0.97 }}
                        transition={{ type: "spring", stiffness: 200, damping: 15 }}
                    >
                        <Link
                            href={`/inbde/quiz/${s.id}`}
                            className="
                group relative block rounded-2xl overflow-hidden
                p-5 border border-[var(--color-accent-secondary)] bg-[var(--color-background)]
                shadow-md hover:shadow-[0_0_25px_var(--color-accent-secondary)]
                transition-all duration-300
              "
                        >
                            {/* Subject name */}
                            <h2 className="font-semibold text-lg text-[var(--color-foreground)] mb-4">
                                {s.name}
                            </h2>

                            {/* Progress ring + percentage */}
                            {p !== undefined ? (
                                <div className="flex items-center gap-4">
                                    <div
                                        className="relative w-12 h-12 rounded-full shrink-0"
                                        style={{
                                            background: `conic-gradient(${ring} ${deg}deg, #1e1b4b ${deg}deg)`,
                                        }}
                                    >
                                        <div className="absolute inset-1 rounded-full bg-[var(--color-background)]" />
                                    </div>

                                    <span className={`text-xl font-medium ${pctColor(p)}`}>
                                        {p}%
                                    </span>
                                </div>
                            ) : (
                                <span className="text-sm text-neutral-400">Not started</span>
                            )}

                            {/* Animated gradient overlay for INBDE theme */}
                            <span
                                className="absolute inset-0 bg-[var(--theme-gradient)] opacity-30 group-hover:opacity-50 transition-opacity pointer-events-none"
                                aria-hidden="true"
                            />
                        </Link>
                    </motion.div>
                );
            })}
        </div>
    );
}