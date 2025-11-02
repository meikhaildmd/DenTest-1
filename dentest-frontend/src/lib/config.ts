// lib/config.ts
export const API =
    process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000/api';

export const MEDIA_BASE =
    process.env.NEXT_PUBLIC_MEDIA_URL || 'http://127.0.0.1:8000';