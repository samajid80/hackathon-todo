/**
 * TagBadge component for displaying task tags.
 *
 * Renders tags as pill badges with Tailwind CSS styling.
 * Supports two sizes: small (sm) and medium (md).
 *
 * Design: specs/001-phase3-task-tags/research.md Section 6
 */

"use client";

interface TagBadgeProps {
  tag: string;
  size?: "sm" | "md";
}

export default function TagBadge({ tag, size = "sm" }: TagBadgeProps) {
  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-3 py-1 text-sm",
  };

  return (
    <span
      className={`
        inline-flex items-center rounded-full
        bg-blue-100 text-blue-800
        font-medium ${sizeClasses[size]}
      `}
    >
      {tag}
    </span>
  );
}
