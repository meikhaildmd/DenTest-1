'use client';
import { Suspense } from 'react';
import SubjectGrid from './SubjectGrid';

/* Define the type inline instead of importing */
interface Subject {
    id: number;
    name: string;
}

export default function SectionClient({ subjects }: { subjects: Subject[] }) {
    return (
        <Suspense fallback={<p className="text-neutral-400">Loading subjects…</p>}>
            <SubjectGrid subjects={subjects} />
        </Suspense>
    );
}