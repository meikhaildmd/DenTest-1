'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';

interface SectionCardProps {
    title: string;
    href: string;
    progress?: number;
}

export default function SectionCard({ title, href, progress }: SectionCardProps) {
    return (
        <motion.div
            whileHover={{ y: -4, scale: 1.02 }}
            transition={{ type: 'spring', stiffness: 200, damping: 15 }}
        >
            <Link
                href={href}
                className="
          group relative block rounded-xl overflow-hidden
          border border-[var(--color-accent-secondary)]/40
          bg-[var(--color-background)]/60 backdrop-blur-sm
          shadow-lg hover:shadow-[0_0_15px_var(--color-accent)/40]
          transition-all duration-300
        "
            >
                {/* Gradient top border strip */}
                <div className="h-1 bg-[var(--theme-gradient)]" />

                <div className="p-5">
                    <h2 className="text-lg font-semibold text-[var(--color-foreground)] mb-2">
                        {title}
                    </h2>

                    {progress !== undefined && (
                        <span className="inline-block text-sm text-[var(--color-accent-secondary)] font-medium">
                            {progress}% complete
                        </span>
                    )}
                </div>

                {/* Animated gradient glow on hover */}
                <div
                    className="
            absolute inset-0 opacity-0 group-hover:opacity-100
            bg-[var(--theme-gradient)] mix-blend-overlay transition-opacity duration-500
          "
                />
            </Link>
        </motion.div>
    );
}