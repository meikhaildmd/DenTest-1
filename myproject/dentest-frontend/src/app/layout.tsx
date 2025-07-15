/* src/app/layout.tsx */
import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';

/* ---- fonts ---- */
const geistSans = Geist({
  subsets: ['latin'],
  variable: '--font-geist-sans',
});
const geistMono = Geist_Mono({
  subsets: ['latin'],
  variable: '--font-geist-mono',
});

/* ---- <head> metadata ---- */
export const metadata: Metadata = {
  title: 'DenTest',
  description: 'Practice for INBDE & ADAT',
};

/* ---- root layout ---- */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="bg-black text-white antialiased">
      <body className={`${geistSans.variable} ${geistMono.variable} min-h-screen`}>
        {children}
      </body>
    </html>
  );
}