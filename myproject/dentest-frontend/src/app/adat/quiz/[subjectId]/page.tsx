/* src/app/inbde/quiz/[subjectId]/page.tsx
   Client page → unwrap params, gather query, mount QuizEngine */
'use client';

import { use } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import QuizEngine from '@/components/QuizEngine';

export default function QuizPage({
  params,
}: {
  params: Promise<{ subjectId: string }>;
}) {
  /* 1 — dynamic segment (promise in Next 15) */
  const { subjectId } = use(params);

  /* 2 — query string values */
  const search = useSearchParams();
  const sectionId = search.get('sectionId') || undefined;  // may be absent
  const isReview = search.get('review') === 'true';

  /* 3 — key so React remounts when route / review mode changes */
  const pathname = usePathname();
  const key = `${pathname}-${isReview}`;

  /* 4 — render the quiz engine */
  return (
    <QuizEngine
      key={key}
      subjectId={subjectId}
      sectionId={sectionId}
      exam="adat"
    />
  );
}