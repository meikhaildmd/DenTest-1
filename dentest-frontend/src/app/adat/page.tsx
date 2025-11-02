/* src/app/adat/page.tsx */
export const dynamic = "force-dynamic";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import AdatClient from "./AdatClient";
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
export default async function AdatHome() {
  const API = process.env.NEXT_PUBLIC_API_BASE_URL;
  let sections: Section[] = [];
  let progress: Record<number, number> = {};

  try {
    const res = await fetch(`${API}/sections/adat/`, { cache: "no-store" });
    if (res.ok) sections = await res.json();
  } catch (e) {
    console.error("Error fetching sections:", e);
  }

  try {
    progress = await getProgress();
  } catch (e) {
    console.error("Error getting progress:", e);
  }

  return (
    <div className="min-h-screen p-6 relative">
      {/* 👇 activates the ADAT color palette */}
      <AdatClient />

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
          ADAT Sections
        </h1>
        <p className="text-[var(--color-accent-secondary)]/80">
          Choose a section to drill focused questions — or build a custom set.
        </p>
      </div>

      {/* SECTIONS GRID */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {sections.map((s) => (
          <SectionCard
            key={s.id}
            title={s.name}
            href={`/adat/section/${s.id}`}
            progress={progress[s.id]}
          />
        ))}
      </div>

      {/* CUSTOM QUIZ BUTTON */}
      <div className="mt-14 text-center">
        <Link href="/custom?exam=adat">
          <GradientButton exam="adat" shimmer glow className="text-lg px-8 py-4">
            Build a Custom ADAT Quiz
          </GradientButton>
        </Link>
      </div>
    </div>
  );
}