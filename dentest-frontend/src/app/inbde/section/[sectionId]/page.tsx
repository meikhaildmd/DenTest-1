/* src/app/inbde/section/[sectionId]/page.tsx */
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';           // tiny icon
import { Suspense } from 'react';
import SubjectGrid from './SubjectGrid';

/* ---------- types ---------- */
interface Subject { id: number; name: string; }
interface SectionWithSubjects {
  id: number;
  name: string;
  subjects: Subject[];
}

/* ---------- page ---------- */
export default async function SectionPage({
  params,
}: {
  params: Promise<{ sectionId: string }>;
}) {
  const { sectionId } = await params;

  const base = process.env.NEXT_PUBLIC_API_BASE_URL!;
  const section: SectionWithSubjects = await fetch(
    `${base}/api/sections/${sectionId}/with-subjects/`,
    { cache: 'no-store' },
  ).then((r) => r.json());

  /* first letter badge colour (blue for INBDE) */
  const badge = (
    <span className="inline-flex h-10 w-10 items-center justify-center
                     rounded-full bg-blue-600 text-white text-xl font-bold">
      {section.name.charAt(0)}
    </span>
  );

  return (
    <div className="min-h-screen px-6 py-10">
      <div className="max-w-5xl mx-auto">

        {/* back link */}
        <Link
          href="/inbde"
          className="mb-6 inline-flex items-center gap-1 text-sm text-blue-400
                     hover:text-blue-300 transition"
        >
          <ArrowLeft size={14} /> Back to INBDE
        </Link>

        {/* header */}
        <div className="flex items-center gap-4 mb-4">
          {badge}
          <h1 className="text-3xl font-bold">{section.name} Subjects</h1>
        </div>

        {/* gradient divider */}
        <div className="h-1 w-28 bg-gradient-to-r from-blue-500 to-purple-500 rounded mb-8" />

        {/* subject grid with progress rings */}
        <Suspense fallback={<p className="text-neutral-400">Loading progress…</p>}>
          <SubjectGrid subjects={section.subjects} />
        </Suspense>
      </div>
    </div>
  );
}