/* src/app/results/page.tsx — unified results page */

'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import { useMemo } from 'react';

export default function ResultsPage() {
    const qs = useSearchParams();
    const nav = useRouter();

    /* ------------------ query params ------------------ */
    const score = Number(qs.get('score'));
    const total = Number(qs.get('total'));
    const subjectId = qs.get('subjectId');
    const sectionId = qs.get('sectionId') || undefined;
    const isCustom = qs.get('custom') === '1';
    const exam = qs.get('exam') || 'inbde';           // inbde | adat

    /* ------------------ visuals ----------------------- */
    const pct = total > 0 ? (score / total) * 100 : 0;
    const pctStr = pct.toFixed(1);

    const { ringFrom, ringTo, emoji } = useMemo(() => {
        if (pct >= 80) return { ringFrom: '#22c55e', ringTo: '#15803d', emoji: '🎉' };
        if (pct >= 50) return { ringFrom: '#facc15', ringTo: '#ca8a04', emoji: '🙂' };
        return { ringFrom: '#ef4444', ringTo: '#991b1b', emoji: '😅' };
    }, [pct]);

    /* ------------------ navigation targets ------------ */
    const done = () => {
        if (sectionId) nav.push(`/${exam}/section/${sectionId}`);
        else nav.push(`/${exam}`);           // main INBDE / ADAT page
    };

    const reviewHref = isCustom
        ? '/custom/quiz?review=true'
        : subjectId
            ? `/${exam}/quiz/${subjectId}?review=true`
            : null;

    /* ------------------ render ------------------------ */
    return (
        <div className="min-h-screen flex items-center justify-center p-6">
            <div className="w-full max-w-md bg-neutral-900 rounded-xl shadow-lg p-8 text-center">
                <div
                    className="mx-auto mb-6 h-32 w-32 rounded-full grid place-items-center"
                    style={{
                        background: `conic-gradient(${ringFrom} 0% ${pct}%, ${ringTo} ${pct}% 100%)`,
                    }}
                >
                    <div className="h-24 w-24 bg-neutral-900 rounded-full grid place-items-center">
                        <span className="text-3xl font-semibold">{pctStr}%</span>
                    </div>
                </div>

                <h1 className="text-3xl font-bold mb-2">{emoji} Test Completed</h1>
                <p className="mb-8">
                    You answered <strong>{score}</strong> of <strong>{total}</strong> correctly
                </p>

                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <button
                        onClick={done}
                        className="flex-grow rounded px-4 py-2 bg-blue-600 hover:bg-blue-700 transition text-white font-medium"
                    >
                        Done
                    </button>

                    {reviewHref && (
                        <a
                            href={reviewHref}
                            className="flex-grow rounded px-4 py-2 border border-neutral-500
                         hover:bg-neutral-800 transition text-neutral-200 font-medium text-center"
                        >
                            Review
                        </a>
                    )}
                </div>
            </div>
        </div>
    );
}