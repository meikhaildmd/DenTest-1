/* components/QuizEngine.tsx */

'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams, usePathname } from 'next/navigation';
import Link from 'next/link';
import { API } from '@/lib/config';

/* ---------- csrf helper ---------- */
function getCookie(name: string) {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(new RegExp('(^|;\\s*)' + name + '=([^;]*)'));
  return match ? decodeURIComponent(match[2]) : null;
}

/* ---------- types ---------- */
export interface Question {
  id: number;
  text: string;
  option1: string;
  option2: string;
  option3: string;
  option4: string;
  correct_option: string;
  explanation: string;
}
type AnswerStatus = { selected: string; isCorrect: boolean };

/* ---------- component ---------- */
export default function QuizEngine({
  subjectId,
  sectionId,
  questions: propQuestions,
  exam = 'inbde',
}: {
  subjectId?: string;
  sectionId?: string;
  questions?: Question[];
  exam?: 'inbde' | 'adat' | 'custom';
}) {
  /* ----- state ----- */
  const [questions, setQuestions] = useState<Question[]>([]);
  const [idx, setIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<number, AnswerStatus>>({});
  const [showExp, setShowExp] = useState(false);

  const router = useRouter();
  const search = useSearchParams();
  const pathname = usePathname();

  const isReview = search.get('review') === 'true';
  const optionMap = { A: 'option1', B: 'option2', C: 'option3', D: 'option4' } as const;

  /* ----- load questions (custom or by subject) ----- */
  useEffect(() => {
    if (propQuestions?.length) {
      setQuestions(propQuestions);
    } else if (subjectId) {
      fetch(`${API}/questions/subject/${subjectId}/`)
        .then(r => r.json())
        .then(setQuestions)
        .catch(err => console.error('Failed to load questions:', err));
    }
  }, [propQuestions, subjectId]);

  /* ----- load answer history ONLY when reviewing ----- */
  useEffect(() => {
    if (!isReview || !subjectId) return;

    fetch(`${API}/user-question-status/subject/${subjectId}/`, {
      credentials: 'include',
    })
      .then(r => (r.status === 403 ? [] : r.json()))
      .then((rows: { question_id: number; last_answer: string; last_was_correct: boolean }[]) => {
        const rec: Record<number, AnswerStatus> = {};
        rows.forEach(d => {
          rec[d.question_id] = {
            selected: d.last_answer,
            isCorrect: d.last_was_correct,
          };
        });
        setAnswers(rec);
      })
      .catch(() => { });
  }, [isReview, subjectId, pathname]);

  /* ----- early render ----- */
  if (!questions.length) {
    return <div className="p-8 text-neutral-300">Loading…</div>;
  }

  const q = questions[idx];

  /* ----- select answer ----- */
  const select = (ltr: string) => {
    if (answers[q.id] || isReview) return;

    const selKey = optionMap[ltr as keyof typeof optionMap];
    const isCorrect = selKey === q.correct_option;

    const updated = { ...answers, [q.id]: { selected: ltr, isCorrect } };
    setAnswers(updated);
    setShowExp(true);

    if (subjectId) {
      fetch(`${API}/user-question-status/update/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') || '',
        },
        credentials: 'include',
        body: JSON.stringify({
          question_id: q.id,
          selected: selKey,
          is_correct: isCorrect,
        }),
      }).catch(() => { });
    }
  };

  /* ----- next / finish ----- */
  const next = () => {
    if (idx + 1 < questions.length) {
      setIdx(idx + 1);
      setShowExp(false); // reset explanation
      return;
    }

    const correct = Object.values(answers).filter(a => a.isCorrect).length;
    const qs = new URLSearchParams({
      score: String(correct),
      total: String(questions.length),
      exam,
    });

    if (subjectId) {
      qs.set('subjectId', subjectId);
      if (sectionId) qs.set('sectionId', sectionId);
    } else {
      qs.set('custom', '1');
    }

    router.push(`/results?${qs.toString()}`);
  };

  /* ---------- render ---------- */
  return (
    <div className="flex flex-col md:flex-row">
      {/* Sidebar */}
      <div className="md:w-20 bg-neutral-900 p-2 flex md:flex-col gap-2 items-center text-sm">
        {/* Logo inside sidebar */}
        <Link
          href="/"
          className="mb-4 text-lg font-bold text-blue-500 hover:text-blue-400"
        >
          DentestPro
        </Link>

        {questions.map((qq, i) => {
          const stat = answers[qq.id];
          const active = i === idx;
          const base = stat
            ? stat.isCorrect ? 'bg-green-500' : 'bg-red-500'
            : 'bg-neutral-800';

          return (
            <button
              key={qq.id}
              onClick={() => { setIdx(i); setShowExp(isReview && !!stat); }}
              className={`w-8 h-8 rounded-full ${base} text-white
                        ${active ? 'ring-2 ring-blue-400' : 'ring-1 ring-neutral-700'}
                        hover:ring-blue-300 transition`}
            >
              {i + 1}
            </button>
          );
        })}
      </div>

      {/* Main panel */}
      <div className="md:w-4/5 max-w-2xl mx-auto mt-10 p-6 bg-neutral-900 rounded-xl shadow text-neutral-100">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">
            Question {idx + 1} / {questions.length}
          </h2>

          {/* Exit button back to section */}
          {sectionId && (
            <Link
              href={`/adat/section/${sectionId}`}
              className="text-sm text-red-500 hover:text-red-400"
            >
              Exit Quiz
            </Link>
          )}
        </div>

        <p className="mb-6">{q.text}</p>

        <div className="space-y-3">
          {(['A', 'B', 'C', 'D'] as const).map(ltr => {
            const optKey = optionMap[ltr];
            const answered = !!answers[q.id];
            const isSel = answers[q.id]?.selected === ltr;
            const isCorrect = q.correct_option === optKey;

            let bg =
              'bg-gray-50 text-neutral-800 dark:bg-neutral-800 dark:text-neutral-100';

            if (answered || isReview) {
              if (isCorrect) {
                bg = 'bg-green-100 text-green-800'; // highlight correct
              }
              if (isSel && !isCorrect) {
                bg = 'bg-red-100 text-red-800'; // user’s wrong answer
              }
              if (!isSel && !isCorrect) {
                bg = 'bg-gray-100 text-neutral-800'; // mute others
              }
            }

            return (
              <button
                key={ltr}
                onClick={() => select(ltr)}
                disabled={answered || isReview}
                className={`block w-full text-left px-4 py-2 border rounded ${bg}`}
              >
                <strong>{ltr}.</strong> {q[optKey]}
              </button>
            );
          })}
        </div>

        {/* explanation */}
        {(showExp || (isReview && answers[q.id])) && (
          <div className="mt-4 p-3 bg-blue-800/20 border-l-4 border-blue-500 rounded">
            <strong>Explanation:</strong>
            <div
              className="mt-1"
              style={{ whiteSpace: 'pre-line' }}
              dangerouslySetInnerHTML={{ __html: q.explanation }}
            />
          </div>
        )}

        <div className="mt-6 text-right">
          <button
            onClick={next}
            className="bg-blue-600 px-4 py-2 rounded text-white hover:bg-blue-700"
          >
            {idx === questions.length - 1 ? 'Finish Test' : 'Next'}
          </button>
        </div>
      </div>
    </div>
  );
}