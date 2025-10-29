'use client';

import { motion } from 'framer-motion';
import React from 'react';
import clsx from 'clsx';

type GradientButtonProps = {
    children: React.ReactNode;
    exam?: 'adat' | 'inbde' | 'home';
    shimmer?: boolean;
    glow?: boolean;
    onClick?: () => void;
    className?: string;
};

export default function GradientButton({
    children,
    exam = 'home',
    shimmer = true,
    glow = false,
    onClick,
    className,
}: GradientButtonProps) {
    const gradientMap = {
        home: 'bg-gradient-to-r from-blue-500 to-green-500',
        adat: 'bg-gradient-to-r from-emerald-800 via-teal-600 to-emerald-400',
        inbde: 'bg-gradient-to-r from-blue-500 via-purple-500 to-fuchsia-500',
    };

    return (
        <motion.button
            whileTap={{ scale: 0.97 }}
            whileHover={{ scale: 1.02 }}
            onClick={onClick}
            className={clsx(
                'relative rounded-full px-6 py-3 font-semibold text-white shadow-lg transition-all duration-300',
                gradientMap[exam],
                glow && 'shadow-[0_0_20px_rgba(0,255,200,0.4)]',
                className
            )}
        >
            {children}

            {shimmer && (
                <span className="absolute inset-0 overflow-hidden rounded-full">
                    <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-[shimmer_2s_infinite]"></span>
                </span>
            )}
        </motion.button>
    );
}