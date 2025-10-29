import { Suspense } from 'react';
import CustomBuilderClient from './CustomBuilderClient';

export default function CustomBuilderPage() {
    return (
        <div className="min-h-screen p-6 bg-neutral-950 text-white">
            <Suspense
                fallback={
                    <p className="text-neutral-400 text-center mt-20 animate-pulse">
                        Loading custom quiz builder…
                    </p>
                }
            >
                <CustomBuilderClient />
            </Suspense>
        </div>
    );
}