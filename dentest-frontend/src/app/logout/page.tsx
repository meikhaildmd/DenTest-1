'use client';
export const dynamic = 'force-dynamic';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiLogout } from '@/lib/auth';

export default function LogoutPage() {
    const router = useRouter();

    useEffect(() => {
        (async () => {
            try {
                await apiLogout();              // <-- real logout happens here
            } catch (e) {
                // swallow; still navigate away
                console.error(e);
            } finally {
                router.replace('/login?loggedout=1');
                router.refresh();               // force revalidate server components / user checks
            }
        })();
    }, [router]);

    return (
        <div className="min-h-screen flex items-center justify-center text-white">
            Signing you out…
        </div>
    );
}