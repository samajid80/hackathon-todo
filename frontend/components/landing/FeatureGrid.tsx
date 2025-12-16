/**
 * FeatureGrid Component
 *
 * Grid layout container for displaying multiple FeatureCard components.
 * Responsive grid that adapts from single-column on mobile to three-column on desktop.
 *
 * @example
 * ```tsx
 * <FeatureGrid>
 *   <FeatureCard icon={...} title="..." description="..." />
 *   <FeatureCard icon={...} title="..." description="..." />
 *   <FeatureCard icon={...} title="..." description="..." />
 * </FeatureGrid>
 * ```
 */

import React from 'react';

export interface FeatureGridProps {
  /** Feature cards to display in the grid */
  children: React.ReactNode;

  /** Optional CSS class for custom styling */
  className?: string;
}

export function FeatureGrid({ children, className = '' }: FeatureGridProps) {
  return (
    <div
      className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 ${className}`}
    >
      {children}
    </div>
  );
}
