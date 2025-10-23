import { Suspense } from 'react';
import ResultsClient from './ResultsClient';

export default function ResultsPage() {
    return (
        <div className="min-h-screen flex items-center justify-center p-6">
            <Suspense fallback={<p className="text-neutral-400">Loading results…</p>}>
                <ResultsClient />
            </Suspense>
        </div>
    );
}