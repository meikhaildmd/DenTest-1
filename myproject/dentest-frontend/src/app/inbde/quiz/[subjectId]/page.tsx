/* src/app/inbde/quiz/[subjectId]/page.tsx
   Client wrapper → unwrap params, read query string, mount QuizEngine */

'use client';

import { use } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import QuizEngine from '@/components/QuizEngine';

export default function QuizPage({
  params,
}: {
  params: Promise<{ subjectId: string }>;
}) {
  /* 1 ─ dynamic segment (Next 15 gives it as a promise) */
  const { subjectId } = use(params);

  /* 2 ─ query-string values */
  const search = useSearchParams();
  const sectionId = search.get('sectionId') || undefined; // may be absent
  const isReview = search.get('review') === 'true';      // optional

  /* 3 ─ ensure remount when path / review flag changes */
  const pathname = usePathname();
  const key = `${pathname}-${isReview}`;

  /* 4 ─ render engine with all needed props */
  return (
    <QuizEngine
      key={key}
      subjectId={subjectId}
      sectionId={sectionId}   /* lets ResultsPage build “Done” link */
      exam="inbde"            /* passed down so next() can send exam=inbde */
    />
  );
}