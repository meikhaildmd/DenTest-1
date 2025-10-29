'use client';
export const dynamic = 'force-dynamic';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import QuizEngine, { Question } from '@/components/QuizEngine';
import GradientButton from '@/components/GradientButton';

export default function CustomQuizClient() {
    const qs = useSearchParams();
    const router = useRouter();

    // exam = ?exam=inbde|adat (default inbde)
    const exam = qs.get('exam') === 'adat' ? 'adat' : 'inbde';
    const [questions, setQuestions] = useState<Question[] | null>(null);

    // load questions once from localStorage
    useEffect(() => {
        const raw = localStorage.getItem('customQuiz');
        if (!raw) {
            router.replace('/custom');
            return;
        }

        try {
            const parsed = JSON.parse(raw) as Question[];
            if (!parsed.length) throw new Error();
            setQuestions(parsed);
        } catch {
            router.replace('/custom');
        }
    }, [router]);

    /* ---------- theme gradients ---------- */
    const themeGradient =
        exam === 'adat'
            ? 'from-emerald-800 via-teal-600 to-emerald-400'
            : 'from-blue-500 via-purple-500 to-fuchsia-500';

    /* ---------- render ---------- */
    if (!questions) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen text-center">
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`text-lg text-white/80 bg-gradient-to-r ${themeGradient} bg-clip-text text-transparent`}
                >
                    Loading custom quiz…
                </motion.div>
            </div>
        );
    }

    return (
        <div className="min-h-screen">
            {/* Fancy header */}
            <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`text-center text-2xl sm:text-3xl font-semibold py-6 bg-gradient-to-r ${themeGradient} text-white shadow-lg`}
            >
                Custom Quiz ({exam.toUpperCase()})
            </motion.div>

            {/* Quiz engine container */}
            <div className="max-w-5xl mx-auto p-6">
                <QuizEngine questions={questions} exam={exam} />
            </div>

            {/* Back button */}
            <div className="flex justify-center mt-10 mb-10">
                <GradientButton
                    exam={exam}
                    onClick={() => router.push(`/custom?exam=${exam}`)}
                    shimmer
                >
                    Back to Builder
                </GradientButton>
            </div>
        </div>
    );
}