import { Suspense } from 'react';
import CustomQuizClient from './CustomQuizClient';

export default function CustomQuizPage() {
    return (
        <div className="min-h-screen p-6">
            <Suspense fallback={<p className="text-neutral-400 text-center mt-20">Loading custom quiz…</p>}>
                <CustomQuizClient />
            </Suspense>
        </div>
    );
}