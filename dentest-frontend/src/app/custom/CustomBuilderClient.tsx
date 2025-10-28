'use client';
export const dynamic = "force-dynamic";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';

/* -------------------------------------------------------------
   Helpers
------------------------------------------------------------- */
function getCookie(name: string): string | null {
    const match = typeof document !== 'undefined'
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
    const examFilter = search.get('exam') ?? 'both'; // ?exam=inbde|adat|both

    const isLoggedIn = typeof document !== 'undefined' && document.cookie.includes('sessionid=');

    /* -------------------------------------------------------------
       Load subjects by section / exam
    ------------------------------------------------------------- */
    useEffect(() => {
        (async () => {
            try {
                const exams = examFilter === 'both' ? ['inbde', 'adat'] : [examFilter];
                const allSubs: Subject[] = [];

                for (const exam of exams) {
                    const sections: Section[] = await fetch(`${API}/sections/${exam}/`).then(r => r.json());
                    for (const sec of sections) {
                        const subs: Subject[] = await fetch(`${API}/sections/${sec.id}/subjects/`).then(r => r.json());
                        subs.forEach(s => allSubs.push({ ...s, section: sec }));
                    }
                }
                setSubjects(allSubs);
            } catch (err) {
                console.error(err);
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
            /* 1️⃣ ensure CSRF cookie exists */
            await fetch(`${API}/csrf/`, { credentials: 'include' });

            /* 2️⃣ get csrftoken */
            const csrf = getCookie('csrftoken');
            if (!csrf) throw new Error('Could not obtain CSRF token.');

            /* 3️⃣ request questions */
            const res = await fetch(`${API}/custom-quiz/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf,
                },
                credentials: 'include', // ✅ important for user progress
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
        } catch (err: any) {
            console.error(err);
            setErrorMsg(err.message || 'Unknown error.');
        } finally {
            setLoading(false);
        }
    };

    /* -------------------------------------------------------------
       Render grouped subjects
    ------------------------------------------------------------- */
    const grouped = subjects.reduce<Record<number, Subject[]>>((acc, s) => {
        (acc[s.section.id] ??= []).push(s);
        return acc;
    }, {});

    return (
        <div className="min-h-screen p-8 max-w-5xl mx-auto">
            <h1 className="text-3xl font-bold mb-6">Build a Custom Quiz</h1>

            {/* SUBJECT PICKER */}
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {Object.entries(grouped).map(([secId, subs]) => (
                    <div key={secId} className="border border-neutral-700 rounded p-4">
                        <h2 className="font-semibold mb-2">{subs[0].section.name}</h2>
                        <ul className="space-y-1">
                            {subs.map(s => (
                                <li key={s.id}>
                                    <label className="inline-flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            className="accent-blue-600"
                                            checked={selected.has(s.id)}
                                            onChange={() => {
                                                const next = new Set(selected);
                                                next.has(s.id) ? next.delete(s.id) : next.add(s.id);
                                                setSelected(next);
                                            }}
                                        />
                                        {s.name}
                                    </label>
                                </li>
                            ))}
                        </ul>
                    </div>
                ))}
            </div>

            {/* FILTER + LIMIT */}
            <div className="mb-8 flex flex-col sm:flex-row items-center gap-6">
                {/* filter options */}
                <div className="flex gap-4">
                    {FILTERS.map(f => {
                        const disabled = !isLoggedIn && f !== 'all';
                        return (
                            <label
                                key={f}
                                className={`inline-flex items-center gap-1 ${disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'
                                    }`}
                            >
                                <input
                                    type="radio"
                                    name="filter"
                                    className="accent-blue-600"
                                    checked={filter === f}
                                    disabled={disabled}
                                    onChange={() => !disabled && setFilter(f)}
                                />
                                {f}
                            </label>
                        );
                    })}
                </div>

                {/* slider */}
                <div className="flex items-center gap-3 w-full max-w-xs">
                    <input
                        type="range"
                        min={5}
                        max={100}
                        value={limit}
                        onChange={e => setLimit(Number(e.target.value))}
                        className="w-full accent-blue-600"
                    />
                    <span className="w-10 text-right">{limit}</span>
                </div>
            </div>

            {/* ERROR + START */}
            {errorMsg && <p className="text-red-400 mb-4">{errorMsg}</p>}

            <button
                disabled={loading || selected.size === 0}
                onClick={start}
                className="px-6 py-3 rounded bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white transition"
            >
                {loading ? 'Building…' : 'Start Quiz'}
            </button>

            <Link href="/" className="ml-6 text-blue-400 hover:underline">
                Cancel
            </Link>
        </div>
    );
}