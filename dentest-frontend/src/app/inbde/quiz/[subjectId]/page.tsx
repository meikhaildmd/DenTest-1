'use client';



import { use } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import QuizEngine from '@/components/QuizEngine';
import { useTheme } from '@/components/ThemeProvider';
import { useEffect } from 'react';

interface PageParams {
  subjectId: string;
}

export default function QuizPage({ params }: { params: Promise<PageParams> }) {
  /* 1️⃣ unwrap Next 15 promise param */
  const { subjectId } = use(params);

  /* 2️⃣ read optional query params */
  const search = useSearchParams();
  const sectionId = search.get('sectionId') || undefined;
  const isReview = search.get('review') === 'true';

  /* 3️⃣ stable key — ensures re-mount between modes */
  const pathname = usePathname();
  const key = `${pathname}-${isReview}`;

  /* 4️⃣ set theme when mounting */
  const { setTheme } = useTheme();
  useEffect(() => {
    setTheme('inbde');
  }, [setTheme]);

  /* 5️⃣ render quiz engine */
  return (
    <QuizEngine
      key={key}
      subjectId={subjectId}
      sectionId={sectionId}
      exam="inbde"
    />
  );
}