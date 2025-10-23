'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

const API = process.env.NEXT_PUBLIC_API_BASE_URL;

export default function LogoutPage() {
    const router = useRouter();

    useEffect(() => {
        async function doLogout() {
            await fetch(`${API}/logout/`, {
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