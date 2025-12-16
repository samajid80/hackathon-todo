/**
 * LandingHero Component
 *
 * Hero section for the landing page with headline, subheadline, and call-to-action buttons.
 * Displays different CTAs based on authentication state.
 *
 * @example
 * ```tsx
 * <LandingHero
 *   headline="Organize Your Tasks Effortlessly"
 *   subheadline="A modern, secure task management application"
 *   isAuthenticated={false}
 * />
 * ```
 */

import React from 'react';
import Link from 'next/link';

export interface LandingHeroProps {
  /** Main headline text (large, attention-grabbing) */
  headline: string;

  /** Supporting subheadline text (explains value proposition) */
  subheadline: string;

  /** Whether user is authenticated (affects CTA buttons) */
  isAuthenticated: boolean;

  /** Optional CSS class for custom styling */
  className?: string;
}

export function LandingHero({
  headline,
  subheadline,
  isAuthenticated,
  className = '',
}: LandingHeroProps) {
  return (
    <section
      className={`bg-gradient-to-r from-blue-50 to-indigo-50 py-16 md:py-20 lg:py-24 ${className}`}
      aria-label="Hero section"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            {headline}
          </h1>
          <p className="text-lg md:text-xl text-gray-700 mb-10 max-w-3xl mx-auto leading-relaxed">
            {subheadline}
          </p>

          {/* Call-to-Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            {isAuthenticated ? (
              <Link
                href="/tasks"
                className="px-8 py-3 bg-primary-600 text-white font-semibold rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors duration-200"
                aria-label="Go to your tasks page"
              >
                Go to Tasks
              </Link>
            ) : (
              <>
                <Link
                  href="/signup"
                  className="px-8 py-3 bg-primary-600 text-white font-semibold rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors duration-200"
                  aria-label="Create a new account"
                >
                  Create Account
                </Link>
                <Link
                  href="/login"
                  className="px-8 py-3 bg-white text-primary-600 font-semibold rounded-md border-2 border-primary-600 hover:bg-primary-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors duration-200"
                  aria-label="Sign in to your account"
                >
                  Sign In
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
