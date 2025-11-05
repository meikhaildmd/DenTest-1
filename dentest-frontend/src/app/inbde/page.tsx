/* src/app/inbde/page.tsx */
export const dynamic = "force-dynamic";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import InbdeClient from "./InbdeClient";
import SectionCard from "@/components/SectionCard";
import GradientButton from "@/components/GradientButton";

/* ---------- types ---------- */
interface Section {
  id: number;
  name: string;
}
interface ProgressRow {
  subject_id: number;
  percent: number;
}

/* ---------- fetch user progress safely ---------- */
async function getProgress(): Promise<Record<number, number>> {
  const API = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!API) {
    console.error("Missing NEXT_PUBLIC_API_BASE_URL");
    return {};
  }

  try {
    const r = await fetch(`${API}/user-progress/`, {
      credentials: "include",
      cache: "no-store",
    });
    if (!r.ok) return {};
    const rows: ProgressRow[] = await r.json();
    return Object.fromEntries(rows.map((p) => [p.subject_id, p.percent]));
  } catch (e) {
    console.error("Error fetching user progress:", e);
    return {};
  }
}

/* ---------- main page ---------- */
export default async function inbdeHome() {
  const API = process.env.NEXT_PUBLIC_API_BASE_URL;
  let sections: Section[] = [];
  let progress: Record<number, number> = {};

  // Fetch inbde sections
  try {
    const res = await fetch(`${API}/sections/inbde/`, { cache: "no-store" });
    if (res.ok) {
      sections = await res.json();
    } else {
      console.error("Failed to fetch inbde sections:", res.status);
      const text = await res.text();
      console.warn("inbde fetch response text:", text);
    }
  } catch (e) {
    console.error("Error fetching inbde sections:", e);
  }

  // Fetch user progress
  try {
    progress = await getProgress();
  } catch (e) {
    console.error("Error getting inbde progress:", e);
  }

  return (
    <div className="min-h-screen p-6 relative">
      {/* 👇 activates the inbde color palette */}
      <InbdeClient />

      {/* BACK BUTTON */}
      <Link
        href="/"
        className="inline-flex items-center gap-2 mb-6 text-[var(--color-accent)] hover:text-[var(--color-accent-secondary)] transition"
      >
        <ArrowLeft size={18} /> Home
      </Link>

      {/* HEADER */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-[var(--color-foreground)] mb-2">
          inbde Sections
        </h1>
        <p className="text-[var(--color-accent-secondary)]/80">
          Choose a section to drill focused questions — or build a custom set.
        </p>
      </div>

      {/* SECTIONS GRID */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {sections.length > 0 ? (
          sections.map((s) => (
            <SectionCard
              key={s.id}
              title={s.name}
              href={`/inbde/section/${s.id}`}
              progress={progress[s.id]}
            />
          ))
        ) : (
          <p className="text-neutral-400 text-center col-span-full">
            No inbde sections found. Check your backend data or import script.
          </p>
        )}
      </div>

      {/* CUSTOM QUIZ BUTTON */}
      <div className="mt-14 text-center">
        <Link href="/custom?exam=inbde">
          <GradientButton exam="inbde" shimmer glow className="text-lg px-8 py-4">
            Build a Custom inbde Quiz
          </GradientButton>
        </Link>
      </div>
    </div>
  );
}