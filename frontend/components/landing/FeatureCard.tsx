/**
 * FeatureCard Component
 *
 * Displays a single feature highlight with an icon, title, and description.
 * Used in the landing page feature grid to showcase key application capabilities.
 *
 * @example
 * ```tsx
 * <FeatureCard
 *   icon={<CheckCircleIcon className="w-6 h-6" />}
 *   title="Task Management"
 *   description="Organize your tasks efficiently with our intuitive interface"
 * />
 * ```
 */

import React from 'react';

export interface FeatureCardProps {
  /** Icon element (React node) displayed at the top of the card */
  icon: React.ReactNode;

  /** Feature title (short, descriptive) */
  title: string;

  /** Feature description (benefit-focused explanation) */
  description: string;

  /** Optional CSS class for custom styling */
  className?: string;
}

export function FeatureCard({
  icon,
  title,
  description,
  className = '',
}: FeatureCardProps) {
  return (
    <div
      className={`bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-300 ${className}`}
    >
      <div className="text-blue-600 mb-4 flex justify-center">{icon}</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2 text-center">
        {title}
      </h3>
      <p className="text-gray-600 text-center leading-relaxed">{description}</p>
    </div>
  );
}
