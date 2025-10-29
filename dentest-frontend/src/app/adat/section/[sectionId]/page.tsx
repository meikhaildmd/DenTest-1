/* src/app/adat/section/[sectionId]/page.tsx */
export const dynamic = "force-dynamic";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import SectionClient from "./SectionClient";

/* ---------- types ---------- */
interface Subject {
  id: number;
  name: string;
}
interface SectionWithSubjects {
  id: number;
  name: string;
  subjects: Subject[];
}

/* ---------- server component ---------- */
export default async function SectionPage({
  params,
}: {
  params: Promise<{ sectionId: string }>;
}) {
  const { sectionId } = await params;

  const base = process.env.NEXT_PUBLIC_API_BASE_URL!;
  const section: SectionWithSubjects = await fetch(
    `${base}/api/sections/${sectionId}/with-subjects/`,
    { cache: "no-store" }
  ).then((r) => r.json());


  const badge = (
    <span
      className="inline-flex h-10 w-10 items-center justify-center
                 rounded-full bg-teal-600 text-white text-xl font-bold shadow-md"
    >
      {section.name.charAt(0)}
    </span>
  );

  /* ---------- render ---------- */
  return (
    <div className="min-h-screen px-6 py-10 bg-neutral-950 text-white">
      <div className="max-w-5xl mx-auto">
        {/* back link */}
        <Link
          href="/adat"
          className="mb-6 inline-flex items-center gap-1 text-sm text-teal-400
                     hover:text-teal-300 transition"
        >
          <ArrowLeft size={14} /> Back to ADAT
        </Link>

        {/* header */}
        <div className="flex items-center gap-4 mb-4">
          {badge}
          <h1 className="text-3xl font-bold">{section.name} Subjects</h1>
        </div>

        {/* gradient divider */}
        <div className="h-1 w-28 bg-gradient-to-r from-teal-500 to-purple-500 rounded mb-8" />

        {/* client-side subject grid */}
        <SectionClient subjects={section.subjects} />
      </div>
    </div>
  );
}