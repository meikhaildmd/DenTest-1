'use client';
import { Suspense } from 'react';
import SubjectGrid from './SubjectGrid';

/* define Subject type locally */
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