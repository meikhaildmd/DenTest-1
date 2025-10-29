'use client';
export const dynamic = 'force-dynamic';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import GradientButton from '@/components/GradientButton';

/* -------------------------------------------------------------
   Helpers
------------------------------------------------------------- */
function getCookie(name: string): string | null {
    const match =
        typeof document !== 'undefined'
            ? document.cookie.match(new RegExp(`(^|;)\\s*${name}=([^;]+)`))
            : null;
    return match ? decodeURIComponent(match[2]) : null;
}

/* -------------------------------------------------------------
   Types
------------------------------------------------------------- */
interface Section { id: number; name: string; }
interface Subject { id: number; name: string; section: Section; }
interface Question { id: number; text: string; }

/* -------------------------------------------------------------
   Constants
------------------------------------------------------------- */
const API = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000/api';
const FILTERS = ['all', 'incorrect', 'correct', 'unanswered'] as const;
type Filter = (typeof FILTERS)[number];

/* -------------------------------------------------------------
   Component
------------------------------------------------------------- */
export default function CustomBuilderClient() {
    const [subjects, setSubjects] = useState<Subject[]>([]);
    const [selected, setSelected] = useState<Set<number>>(new Set());
    const [filter, setFilter] = useState<Filter>('all');
    const [limit, setLimit] = useState<number>(20);
    const [loading, setLoading] = useState(false);
    const [errorMsg, setErrorMsg] = useState<string | null>(null);

    const router = useRouter();
    const search = useSearchParams();
    const examFilter = search.get('exam') ?? 'both';

    const isLoggedIn =
        typeof document !== 'undefined' && document.cookie.includes('sessionid=');

    /* -------------------------------------------------------------
       THEME detection (ADAT / INBDE / BOTH)
    ------------------------------------------------------------- */
    const themeGradient =
        examFilter === 'adat'
            ? 'from-emerald-800 via-teal-600 to-emerald-400'
            : examFilter === 'inbde'
                ? 'from-blue-500 via-purple-500 to-fuchsia-500'
                : 'from-blue-500 via-green-500 to-teal-400';

    /* -------------------------------------------------------------
       Load subjects by section / exam
    ------------------------------------------------------------- */
    useEffect(() => {
        (async () => {
            try {
                const exams = examFilter === 'both' ? ['inbde', 'adat'] : [examFilter];
                const allSubs: Subject[] = [];

                for (const exam of exams) {
                    const sections: Section[] = await fetch(`${API}/sections/${exam}/`).then((r) =>
                        r.json()
                    );
                    for (const sec of sections) {
                        const subs: Subject[] = await fetch(
                            `${API}/sections/${sec.id}/subjects/`
                        ).then((r) => r.json());
                        subs.forEach((s) => allSubs.push({ ...s, section: sec }));
                    }
                }
                setSubjects(allSubs);
            } catch (err) {
                console.error('Error loading subjects:', err);
                setErrorMsg('Failed to load subjects.');
            }
        })();
    }, [examFilter]);

    /* -------------------------------------------------------------
       Start quiz
    ------------------------------------------------------------- */
    const start = async () => {
        setErrorMsg(null);
        setLoading(true);

        try {
            await fetch(`${API}/csrf/`, { credentials: 'include' });
            const csrf = getCookie('csrftoken');
            if (!csrf) throw new Error('Could not obtain CSRF token.');

            const res = await fetch(`${API}/custom-quiz/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf,
                },
                credentials: 'include',
                body: JSON.stringify({
                    subject_ids: Array.from(selected),
                    filter,
                    limit,
                }),
            });

            if (!res.ok) {
                const data = await res.json().catch(() => ({}));
                throw new Error(data.detail || data.error || 'Quiz creation failed.');
            }

            const questions: Question[] = await res.json();
            localStorage.setItem('customQuiz', JSON.stringify(questions));
            router.push('/custom/quiz');
        } catch (err: unknown) {
            console.error('Quiz start error:', err);
            if (err instanceof Error) setErrorMsg(err.message);
            else setErrorMsg('Unknown error.');
        } finally {
            setLoading(false);
        }
    };

    /* -------------------------------------------------------------
       Group subjects for display
    ------------------------------------------------------------- */
    const grouped = subjects.reduce<Record<number, Subject[]>>((acc, s) => {
        (acc[s.section.id] ??= []).push(s);
        return acc;
    }, {});

    /* -------------------------------------------------------------
       Render
    ------------------------------------------------------------- */
    return (
        <div className="min-h-screen p-8 max-w-5xl mx-auto">
            {/* Header gradient */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`mx-auto mb-10 w-fit rounded-full py-3 px-8 text-xl sm:text-2xl font-semibold text-white shadow-lg bg-gradient-to-r ${themeGradient} animate-slide-down`}
            >
                Build Your Custom Quiz
            </motion.div>

            {/* SUBJECT PICKER */}
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {Object.entries(grouped).map(([secId, subs]) => (
                    <motion.div
                        key={secId}
                        whileHover={{ scale: 1.03 }}
                        className="border border-neutral-700 rounded-xl p-4 bg-neutral-900/60 hover:bg-neutral-800 transition-all duration-200"
                    >
                        <h2 className="font-semibold mb-3 text-white/90">
                            {subs[0].section.name}
                        </h2>
                        <ul className="space-y-2">
                            {subs.map((s) => (
                                <li key={s.id}>
                                    <label
                                        className={`inline-flex items-center gap-2 cursor-pointer transition ${selected.has(s.id)
                                            ? 'text-emerald-300'
                                            : 'text-neutral-300 hover:text-white'
                                            }`}
                                    >
                                        <input
                                            type="checkbox"
                                            className="accent-emerald-500"
                                            checked={selected.has(s.id)}
                                            onChange={() => {
                                                const next = new Set(selected);
                                                next.has(s.id) ? void next.delete(s.id) : next.add(s.id);
                                                setSelected(next);
                                            }}
                                        />
                                        {s.name}
                                    </label>
                                </li>
                            ))}
                        </ul>
                    </motion.div>
                ))}
            </div>

            {/* FILTER + LIMIT */}
            <div className="mb-10 flex flex-col sm:flex-row items-center justify-between gap-6">
                {/* Filter radio chips */}
                <div className="flex gap-4">
                    {FILTERS.map((f) => {
                        const disabled = !isLoggedIn && f !== 'all';
                        return (
                            <button
                                key={f}
                                disabled={disabled}
                                onClick={() => !disabled && setFilter(f)}
                                className={`px-4 py-1.5 rounded-full text-sm font-medium transition ${filter === f
                                    ? 'bg-gradient-to-r from-emerald-600 to-teal-500 text-white'
                                    : 'bg-neutral-800 text-neutral-300 hover:bg-neutral-700'
                                    } ${disabled ? 'opacity-40 cursor-not-allowed' : ''}`}
                            >
                                {f}
                            </button>
                        );
                    })}
                </div>

                {/* Range slider */}
                <div className="flex items-center gap-3 w-full max-w-xs">
                    <input
                        type="range"
                        min={5}
                        max={100}
                        value={limit}
                        onChange={(e) => setLimit(Number(e.target.value))}
                        className="w-full accent-emerald-500"
                    />
                    <span className="w-10 text-right text-neutral-300">{limit}</span>
                </div>
            </div>

            {/* ERROR + START */}
            {errorMsg && (
                <p className="text-red-400 mb-4 animate-pulse text-center">{errorMsg}</p>
            )}

            <div className="flex justify-center gap-6 mt-8">
                <GradientButton
                    onClick={start}
                    exam={examFilter === 'inbde' ? 'inbde' : examFilter === 'adat' ? 'adat' : 'home'}
                    glow
                >
                    {loading ? 'Building…' : 'Start Quiz'}
                </GradientButton>

                <Link href="/" className="mt-2">
                    <GradientButton exam="home" shimmer={false}>
                        Cancel
                    </GradientButton>
                </Link>
            </div>
        </div>
    );
}