/**
 * Priority Badge Component (T067)
 *
 * Features:
 * - Small badge showing priority level
 * - Color coding: low=gray, medium=blue, high=red
 * - Responsive text size
 * - Used in TaskCard and TaskTable
 */

import React from "react";
import { Priority, getPriorityLabel } from "@/types/task";

export interface PriorityBadgeProps {
  priority: Priority;
  className?: string;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({
  priority,
  className = "",
}) => {
  const baseStyles =
    "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium";

  const priorityStyles = {
    low: "bg-gray-100 text-gray-800",
    medium: "bg-blue-100 text-blue-800",
    high: "bg-red-100 text-red-800",
  };

  return (
    <span
      className={`${baseStyles} ${priorityStyles[priority]} ${className}`}
      aria-label={`Priority: ${getPriorityLabel(priority)}`}
    >
      {getPriorityLabel(priority)}
    </span>
  );
};
