export async function apiLogout() {
    const base = process.env.NEXT_PUBLIC_API_BASE_URL!;
    // 1) fetch CSRF (sets csrftoken cookie and returns it in JSON)
    const csrf = await fetch(`${base}/csrf/`, { credentials: 'include', cache: 'no-store' });
    const data = await csrf.json(); // expect: { csrftoken: "..." }
    const token = data?.csrftoken;
    if (!token) throw new Error('Missing CSRF token');

    // 2) POST logout with CSRF + cookies
    const r = await fetch(`${base}/logout/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': token },
        credentials: 'include',
    });

    if (!r.ok) throw new Error('Logout failed');
}