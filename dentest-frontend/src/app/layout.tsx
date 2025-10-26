/* src/app/layout.tsx */
import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import Script from 'next/script'; // ✅ Needed for Google Analytics
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
  title: 'ToothPrep',
  description: 'Master the INBDE & ADAT with AI-powered preparation tools',
};

/* ---- root layout ---- */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const gaId = process.env.NEXT_PUBLIC_GA_ID;

  return (
    <html lang="en" className="bg-black text-white antialiased">
      <head>
        {/* ✅ Google Analytics tracking */}
        {gaId && (
          <>
            <Script
              async
              src={`https://www.googletagmanager.com/gtag/js?id=${gaId}`}
            />
            <Script id="google-analytics">
              {`
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', '${gaId}', {
                  page_path: window.location.pathname,
                });
              `}
            </Script>
          </>
        )}
      </head>

      <body
        className={`${geistSans.variable} ${geistMono.variable} min-h-screen`}
      >
        {children}
      </body>
    </html>
  );
}