'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function LogoutPage() {
    const router = useRouter();

    useEffect(() => {
        async function doLogout() {
            await fetch('http://127.0.0.1:8000/api/logout/', {
                method: 'POST',
                credentials: 'include',
            });
            router.push('/login');
        }
        doLogout();
    }, [router]);

    return (
        <div className="min-h-screen flex items-center justify-center text-white">
            Logging out…
        </div>
    );
}