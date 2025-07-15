/* src/app/custom/page.tsx
   Client-side page – lets user build a custom quiz */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';

/* read a cookie value */
function getCookie(name: string): string | null {
    const m = typeof document !== 'undefined'
        ? document.cookie.match(new RegExp(`(^|;)\\s*${name}=([^;]+)`))
        : null;
    return m ? decodeURIComponent(m[2]) : null;
}

interface Section { id: number; name: string; }
interface Subject { id: number; name: string; section: { id: number; name: string } }
interface Question { id: number; text: string; }

const API = 'http://127.0.0.1:8000/api';
const FILTERS = ['all', 'incorrect', 'correct', 'unanswered'] as const;
type Filter = (typeof FILTERS)[number];

export default function CustomBuilder() {
    const [subjects, setSubjects] = useState<Subject[]>([]);
    const [selected, setSelected] = useState<Set<number>>(new Set());
    const [filter, setFilter] = useState<Filter>('all');
    const [limit, setLimit] = useState(20);
    const [loading, setLoading] = useState(false);
    const [errorMsg, setErrorMsg] = useState<string | null>(null);

    const router = useRouter();

    /* --- tiny helper: guest check via sessionid cookie --- */
    const isLoggedIn =
        typeof document !== 'undefined' && document.cookie.includes('sessionid=');

    /* --- exam filter from ?exam=inbde|adat|both --- */
    const search = useSearchParams();
    const examFilter = search.get('exam') ?? 'both';   // default = both
    useEffect(() => {
        (async () => {
            try {
                const exams = examFilter === 'both'
                    ? ['inbde', 'adat']
                    : [examFilter];            // only the chosen exam
                const list: Subject[] = [];

                for (const exam of exams) {
                    const secs: Section[] = await fetch(`${API}/sections/${exam}/`).then(r => r.json());

                    for (const sec of secs) {
                        const subs: Subject[] = await fetch(`${API}/sections/${sec.id}/subjects/`).then(r => r.json());
                        subs.forEach(s => list.push({ ...s, section: sec }));
                    }
                }
                setSubjects(list);
            } catch {
                setErrorMsg('Failed to load subjects');
            }
        })();
    }, []);

    /* --- UI handlers --- */
    const toggleSubject = (id: number) => {
        const next = new Set(selected);
        next.has(id) ? next.delete(id) : next.add(id);
        setSelected(next);
    };

    const start = async () => {
        setErrorMsg(null);
        setLoading(true);
        try {
            /* 1. ensure csrftoken cookie exists */
            await fetch('http://127.0.0.1:8000/api/csrf/', { credentials: 'include' });

            /* 2. read it */
            const csrf = getCookie('csrftoken');
            if (!csrf) {                       // safety check
                setErrorMsg('Could not obtain CSRF token');
                setLoading(false);
                return;
            }
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

            if (!res.ok) throw new Error((await res.json()).detail || 'Error');

            const questions: Question[] = await res.json();
            localStorage.setItem('customQuiz', JSON.stringify(questions));
            router.push('/custom/quiz');
        } catch (err: any) {
            setErrorMsg(err.message || 'Unknown error');
        } finally {
            setLoading(false);
        }
    };

    /* group by section for nicer layout */
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
                                            onChange={() => toggleSubject(s.id)}
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
                {/* correctness filter */}
                <div className="flex gap-4">
                    {FILTERS.map(f => {
                        const disabled = !isLoggedIn && f !== 'all';
                        return (
                            <label
                                key={f}
                                className={`inline-flex items-center gap-1 ${disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}`}
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

            <Link href="/" className="ml-6 text-blue-400 hover:underline">Cancel</Link>
        </div>
    );
}