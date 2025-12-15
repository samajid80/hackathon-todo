/**
 * Status Badge Component (T068)
 *
 * Features:
 * - Small badge showing status
 * - Pending: orange background, orange text
 * - Completed: green background, green text
 * - Icon: checkmark for completed, circle for pending
 * - Used in TaskCard and TaskTable
 * - Responsive text size
 */

import React from "react";
import { Status, getStatusLabel } from "@/types/task";

export interface StatusBadgeProps {
  status: Status;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  className = "",
}) => {
  const baseStyles =
    "inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium";

  const statusStyles = {
    pending: "bg-orange-100 text-orange-800",
    completed: "bg-green-100 text-green-800",
  };

  const icon =
    status === "completed" ? (
      // Checkmark icon
      <svg
        className="w-3 h-3"
        fill="currentColor"
        viewBox="0 0 20 20"
        aria-hidden="true"
      >
        <path
          fillRule="evenodd"
          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
          clipRule="evenodd"
        />
      </svg>
    ) : (
      // Circle icon
      <svg
        className="w-3 h-3"
        fill="currentColor"
        viewBox="0 0 20 20"
        aria-hidden="true"
      >
        <circle cx="10" cy="10" r="6" />
      </svg>
    );

  return (
    <span
      className={`${baseStyles} ${statusStyles[status]} ${className}`}
      aria-label={`Status: ${getStatusLabel(status)}`}
    >
      {icon}
      {getStatusLabel(status)}
    </span>
  );
};
