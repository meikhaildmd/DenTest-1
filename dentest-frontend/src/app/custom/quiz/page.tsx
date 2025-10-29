import { Suspense } from 'react';
import CustomQuizClient from './CustomQuizClient';

export default function CustomQuizPage() {
    return (
        <div className="min-h-screen bg-neutral-950 text-white">
            <Suspense
                fallback={
                    <p className="text-neutral-400 text-center mt-20 animate-pulse">
                        Loading custom quiz…
                    </p>
                }
            >
                <CustomQuizClient />
            </Suspense>
        </div>
    );
}