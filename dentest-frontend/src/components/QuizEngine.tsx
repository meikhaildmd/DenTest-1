'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter, useSearchParams, usePathname } from 'next/navigation';
import Link from 'next/link';
import { AnimatePresence, motion } from 'framer-motion';
import clsx from 'clsx';
import GradientButton from '@/components/GradientButton';
import { API } from '@/lib/config';
import { MEDIA_BASE } from "@/lib/config";
import Image from "next/image";

/* ---------- csrf helper ---------- */
function getCookie(name: string) {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(new RegExp('(^|;\\s*)' + name + '=([^;]*)'));
  return match ? decodeURIComponent(match[2]) : null;
}



function fullMediaUrl(url?: string | null): string | null {
  if (!url) return null;
  if (url.startsWith("http")) return url; // already full
  if (url.startsWith("/")) return `${MEDIA_BASE}${url}`;
  return `${MEDIA_BASE}/${url}`;
}

/* ---------- types ---------- */
export interface Question {
  id: number;
  text: string;
  option1: string;
  option2: string;
  option3: string;
  option4: string;
  correct_option: 'option1' | 'option2' | 'option3' | 'option4';
  explanation: string;
  question_image?: string | null;
  question_image_url?: string | null;
  explanation_image?: string | null;
  explanation_image_url?: string | null;
}
type Letter = 'A' | 'B' | 'C' | 'D';
type AnswerStatus = { selected: Letter; isCorrect: boolean };

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

  const optionMap = useMemo(
    () => ({ A: 'option1', B: 'option2', C: 'option3', D: 'option4' } as const),
    []
  );

  /* ----- theme helpers ----- */
  const themeExam = exam === 'custom' ? 'home' : exam;
  const themeAccent =
    exam === 'adat'
      ? 'from-emerald-700 via-teal-600 to-emerald-400'
      : 'from-blue-600 via-purple-600 to-fuchsia-500';

  /* ----- load questions (custom or by subject) ----- */
  useEffect(() => {
    if (propQuestions?.length) {
      setQuestions(propQuestions);
    } else if (subjectId) {
      fetch(`${API}/questions/subject/${subjectId}/`)
        .then((r) => r.json())
        .then(setQuestions)
        .catch((err) => console.error('Failed to load questions:', err));
    }
  }, [propQuestions, subjectId]);

  /* ----- load answer history ONLY when reviewing ----- */
  useEffect(() => {
    if (!isReview || !subjectId) return;

    fetch(`${API}/user-question-status/subject/${subjectId}/`, {
      credentials: 'include',
    })
      .then((r) => (r.status === 403 ? [] : r.json()))
      .then(
        (
          rows: {
            question_id: number;
            last_answer: Letter;
            last_was_correct: boolean;
          }[]
        ) => {
          const rec: Record<number, AnswerStatus> = {};
          rows.forEach((d) => {
            rec[d.question_id] = {
              selected: d.last_answer,
              isCorrect: d.last_was_correct,
            };
          });
          setAnswers(rec);
        }
      )
      .catch(() => { });
  }, [isReview, subjectId, pathname]);

  /* ----- early render ----- */
  if (!questions.length) {
    return (
      <div className="p-8 text-neutral-300">
        <div className="animate-pulse h-5 w-32 rounded bg-neutral-800 mb-3" />
        <div className="animate-pulse h-5 w-44 rounded bg-neutral-800 mb-3" />
        <div className="animate-pulse h-5 w-24 rounded bg-neutral-800" />
      </div>
    );
  }

  const q = questions[idx];

  /* ----- select answer ----- */
  const select = (ltr: Letter) => {
    if (answers[q.id] || isReview) return;

    const selKey = optionMap[ltr];
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
      setShowExp(false);
      return;
    }

    const correct = Object.values(answers).filter((a) => a.isCorrect).length;
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

  /* ----- helpers for styling ----- */
  const exitHref =
    exam === 'adat'
      ? sectionId
        ? `/adat/section/${sectionId}`
        : '/adat'
      : exam === 'inbde'
        ? sectionId
          ? `/inbde/section/${sectionId}`
          : '/inbde'
        : '/';

  const answerBg = (ltr: Letter) => {
    const optKey = optionMap[ltr];
    const answered = !!answers[q.id];
    const isSel = answers[q.id]?.selected === ltr;
    const isCorrect = q.correct_option === optKey;

    let base =
      'bg-neutral-900/60 border border-neutral-700 text-neutral-100 hover:border-neutral-500';

    if (answered || isReview) {
      if (isCorrect) {
        base =
          'text-white ring-1 ring-white/10 ' +
          (exam === 'adat'
            ? 'bg-gradient-to-r from-emerald-700 via-teal-600 to-emerald-500'
            : 'bg-gradient-to-r from-blue-600 via-purple-600 to-fuchsia-500');
      }
      if (isSel && !isCorrect) {
        base =
          'bg-gradient-to-r from-red-700 via-rose-700 to-red-600 text-white ring-1 ring-rose-300/20';
      }
      if (!isSel && !isCorrect) {
        base = 'bg-neutral-900/70 border border-neutral-800 text-neutral-300';
      }
    }

    return base;
  };

  /* ---------- render ---------- */
  return (
    <div className="flex flex-col md:flex-row">
      {/* Sidebar */}
      <aside className="md:w-24 bg-neutral-950/80 p-2 md:p-3 flex md:flex-col gap-2 items-center text-sm backdrop-blur">
        <Link
          href="/"
          className={clsx(
            'mb-3 text-lg font-extrabold tracking-tight',
            exam === 'adat' ? 'text-emerald-300' : 'text-blue-300'
          )}
        >
          ToothPrep
        </Link>

        {questions.map((qq, i) => {
          const stat = answers[qq.id];
          const active = i === idx;
          const ok = stat?.isCorrect;
          const wrong = stat && !stat.isCorrect;

          const base = clsx(
            'w-10 h-10 rounded-full grid place-items-center font-semibold select-none transition',
            'shadow-sm hover:scale-105',
            active && (exam === 'adat' ? 'ring-2 ring-emerald-400' : 'ring-2 ring-blue-400'),
            !stat && 'bg-neutral-800/80 text-neutral-200 ring-1 ring-neutral-700',
            ok &&
            'text-white shadow-[0_0_18px_rgba(16,185,129,0.35)] bg-gradient-to-b from-green-500 to-emerald-600',
            wrong &&
            'text-white shadow-[0_0_18px_rgba(244,63,94,0.35)] bg-gradient-to-b from-rose-500 to-red-600'
          );

          return (
            <button
              key={qq.id}
              onClick={() => {
                setIdx(i);
                setShowExp(isReview && !!stat);
              }}
              className={base}
              aria-label={`Go to question ${i + 1}`}
            >
              {i + 1}
            </button>
          );
        })}
      </aside>

      {/* Main panel */}
      <main className="md:flex-1 max-w-3xl mx-auto mt-6 md:mt-10 px-4 md:px-6 w-full">
        <motion.div
          key={q.id}
          initial={{ y: 8, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.25 }}
          className={clsx(
            'rounded-2xl p-6 md:p-7 shadow-lg border',
            'bg-neutral-900/80 border-neutral-800 backdrop-blur'
          )}
        >
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg md:text-xl font-semibold tracking-tight">
              Question {idx + 1} / {questions.length}
            </h2>

            <GradientButton
              exam={themeExam as 'inbde' | 'adat' | 'home' | undefined}
              shimmer={false}
              onClick={() => router.push(exitHref)}
              className="px-4 py-2 text-sm"
            >
              Exit
            </GradientButton>
          </div>

          {/* Question text */}
          <div className="mb-6">
            <div
              className={clsx(
                'inline-block rounded-full px-3 py-1 text-xs font-bold mb-3',
                'text-white',
                `bg-gradient-to-r ${themeAccent}`
              )}
            >
              {exam.toUpperCase()}
            </div>
            <p className="leading-relaxed text-neutral-100">{q.text}</p>
            {(q.question_image || q.question_image_url) && (
              <div className="relative w-full max-w-md mx-auto my-4 aspect-auto">
                <Image
                  src={fullMediaUrl(q.question_image_url || q.question_image)!}
                  alt="Question diagram"
                  className="rounded-lg border border-neutral-800 object-contain"
                  width={600}
                  height={400}
                  priority={false}
                />
              </div>
            )}
          </div>

          {/* Options */}
          <div className="space-y-3">
            {(Object.keys(optionMap) as Letter[]).map((ltr) => {
              const optKey = optionMap[ltr];
              const answered = !!answers[q.id];
              const isSel = answers[q.id]?.selected === ltr;
              const isCorrect = q.correct_option === optKey;

              return (
                <motion.button
                  key={ltr}
                  whileHover={!answered ? { scale: 1.01 } : undefined}
                  whileTap={!answered ? { scale: 0.99 } : undefined}
                  onClick={() => select(ltr)}
                  disabled={answered || isReview}
                  className={clsx(
                    'relative block w-full text-left px-4 py-3 rounded-xl border transition-colors',
                    answerBg(ltr),
                    (answered || isReview) && (isCorrect || isSel)
                      ? 'shadow-[0_0_0_1px_rgba(255,255,255,0.07)_inset,0_0_30px_rgba(255,255,255,0.05)]'
                      : 'hover:shadow-[0_0_0_1px_rgba(255,255,255,0.05)_inset]'
                  )}
                >
                  <span className="font-bold mr-2">{ltr}.</span>
                  {q[optKey]}
                  <AnimatePresence>
                    {(isCorrect || (isSel && !isCorrect)) && (answered || isReview) && (
                      <motion.span
                        initial={{ x: '-120%' }}
                        animate={{ x: '140%' }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 1.15, ease: 'easeOut' }}
                        className="pointer-events-none absolute inset-y-0 -left-10 w-24 skew-x-[-20deg] bg-white/10"
                        style={{ maskImage: 'linear-gradient(90deg, transparent, black, transparent)' }}
                      />
                    )}
                  </AnimatePresence>
                </motion.button>
              );
            })}
          </div>

          {/* Explanation */}
          <AnimatePresence initial={false} mode="wait">
            {(showExp || (isReview && answers[q.id])) && (
              <motion.div
                key="explanation"
                initial={{ height: 0, opacity: 0, y: -6 }}
                animate={{ height: 'auto', opacity: 1, y: 0 }}
                exit={{ height: 0, opacity: 0, y: -6 }}
                transition={{ duration: 0.25 }}
                className="mt-5 overflow-hidden"
              >
                <div
                  className={clsx(
                    'rounded-xl p-4 border',
                    'bg-neutral-900/70 border-neutral-800'
                  )}
                >
                  <div
                    className="prose prose-invert max-w-none prose-p:my-2 prose-strong:font-semibold"
                    style={{ whiteSpace: 'pre-line' }}
                    dangerouslySetInnerHTML={{ __html: q.explanation }}
                  />
                </div>
                {(q.explanation_image || q.explanation_image_url) && (
                  <div className="relative w-full max-w-md mx-auto mt-4 aspect-auto">
                    <Image
                      src={fullMediaUrl(q.explanation_image_url || q.explanation_image)!}
                      alt="Explanation diagram"
                      className="rounded-lg border border-neutral-800 object-contain"
                      width={600}
                      height={400}
                      priority={false}
                    />
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Actions */}
          <div className="mt-6 flex items-center justify-end gap-3">
            {sectionId && (
              <GradientButton
                exam={themeExam as 'inbde' | 'adat' | 'home' | undefined}
                shimmer={false}
                onClick={() => router.push(exitHref)}
                className="px-5 py-2"
              >
                Exit Section
              </GradientButton>
            )}

            <GradientButton
              exam={themeExam as 'inbde' | 'adat' | 'home' | undefined}
              shimmer
              glow
              onClick={next}
              className="px-6 py-2"
            >
              {idx === questions.length - 1 ? 'Finish Test' : 'Next'}
            </GradientButton>
          </div>
        </motion.div>

        <div className={clsx('mt-8 h-1 rounded-full w-40', `bg-gradient-to-r ${themeAccent}`)} />
      </main>
    </div>
  );
}