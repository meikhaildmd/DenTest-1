'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import QuizEngine, { Question } from '@/components/QuizEngine';

export default function CustomQuizClient() {
    const qs = useSearchParams();
    const router = useRouter();

    // exam comes from ?exam=inbde|adat (default to inbde)
    const exam = qs.get('exam') === 'adat' ? 'adat' : 'inbde';

    // questions array from localStorage
    const [questions, setQuestions] = useState<Question[] | null>(null);

    // load once on mount
    useEffect(() => {
        const raw = localStorage.getItem('customQuiz');
        if (!raw) {
            router.replace('/custom'); // nothing stored → back to builder
            return;
        }

        try {
            const parsed = JSON.parse(raw) as Question[];
            if (!parsed.length) throw new Error();
            setQuestions(parsed);
        } catch {
            router.replace('/custom'); // malformed → back to builder
        }
    }, [router]);

    // show nothing (or loader) until we have questions
    if (!questions) {
        return <p className="text-center text-neutral-400 mt-20">Loading questions…</p>;
    }

    // render quiz engine in custom mode
    return (
        <QuizEngine
            questions={questions}   // custom-quiz questions
            exam={exam}             // "inbde" | "adat" passed to results page
        />
    );
}