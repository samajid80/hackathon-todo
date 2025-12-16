/**
 * Landing Page - Home
 *
 * This is the main entry point for the application. It displays different
 * content based on authentication state:
 *
 * - Loading: Shows skeleton while checking authentication status
 * - Authenticated: Shows "Go to Tasks" button and welcome message
 * - Unauthenticated: Shows modern landing page with feature highlights
 *
 * Authentication state is detected using the useAuth() hook which wraps
 * Better-Auth's useSession() to prevent flash of unauthenticated content (FOUC).
 */

'use client';

import React from 'react';
import { useAuth } from '@/lib/hooks/useAuth';
import { LandingHero } from '@/components/landing/LandingHero';
import { FeatureGrid } from '@/components/landing/FeatureGrid';
import { FeatureCard } from '@/components/landing/FeatureCard';

/**
 * Feature content data - highlights key application capabilities
 */
const features = [
  {
    title: 'Task Management',
    description: 'Create, update, and organize your tasks with an intuitive interface designed for productivity',
    icon: (
      <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
    ),
  },
  {
    title: 'Filter & Sort',
    description: 'Find what you need quickly with powerful filtering and sorting options that adapt to your workflow',
    icon: (
      <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
      </svg>
    ),
  },
  {
    title: 'Secure & Private',
    description: 'Your tasks are protected with enterprise-grade authentication and encrypted storage',
    icon: (
      <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
    ),
  },
];

/**
 * Loading Skeleton - Displayed while authentication state is being determined
 */
function LoadingSkeleton() {
  return (
    <div className="animate-pulse">
      {/* Hero skeleton */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 py-16 md:py-20 lg:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="h-16 bg-gray-300 rounded-lg w-3/4 mx-auto mb-6"></div>
            <div className="h-6 bg-gray-200 rounded w-1/2 mx-auto mb-10"></div>
            <div className="flex gap-4 justify-center">
              <div className="h-12 bg-gray-300 rounded-md w-40"></div>
              <div className="h-12 bg-gray-200 rounded-md w-32"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Features skeleton */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white p-6 rounded-lg shadow-sm">
              <div className="h-12 w-12 bg-gray-200 rounded-full mx-auto mb-4"></div>
              <div className="h-6 bg-gray-200 rounded w-3/4 mx-auto mb-2"></div>
              <div className="h-4 bg-gray-100 rounded w-full mb-1"></div>
              <div className="h-4 bg-gray-100 rounded w-5/6 mx-auto"></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * Unauthenticated View - Modern landing page for visitors
 */
function UnauthenticatedView() {
  return (
    <div className="animate-fade-in">
      <LandingHero
        headline="Organize Your Tasks Effortlessly"
        subheadline="A modern, secure task management application built for productivity and simplicity"
        isAuthenticated={false}
      />

      {/* Feature highlights section */}
      <section className="py-16 md:py-20 bg-white" aria-label="Key features">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Everything You Need to Stay Organized
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Simple, powerful features that help you focus on what matters most
            </p>
          </div>

          <FeatureGrid>
            {features.map((feature) => (
              <FeatureCard
                key={feature.title}
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
              />
            ))}
          </FeatureGrid>
        </div>
      </section>
    </div>
  );
}

/**
 * Authenticated View - Welcome back message with CTA to tasks
 */
function AuthenticatedView() {
  const { user } = useAuth();

  return (
    <div className="animate-fade-in">
      <LandingHero
        headline={`Welcome Back${user?.name ? `, ${user.name}` : ''}!`}
        subheadline="Ready to tackle your tasks? Jump right in and stay productive."
        isAuthenticated={true}
      />

      {/* Quick stats or recent activity could go here in the future */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-lg text-gray-600">
            Access your tasks, manage priorities, and stay on top of your to-do list.
          </p>
        </div>
      </section>
    </div>
  );
}

/**
 * Main Home Page Component
 *
 * Detects authentication state and renders appropriate view:
 * - LoadingSkeleton while checking auth status (prevents FOUC)
 * - AuthenticatedView if user is logged in
 * - UnauthenticatedView if user is not logged in
 */
export default function HomePage() {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading skeleton while authentication state is being determined
  // This prevents flash of unauthenticated content (FOUC)
  if (isLoading) {
    return <LoadingSkeleton />;
  }

  // Show appropriate view based on authentication status
  if (isAuthenticated) {
    return <AuthenticatedView />;
  }

  return <UnauthenticatedView />;
}
