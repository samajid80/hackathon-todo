/**
 * Task Filters Component (T083, T088)
 *
 * Features:
 * - Button group with 4 filter buttons: All, Pending, Completed, Overdue
 * - Active button highlighted
 * - Clicking button updates filter state
 * - Pass selected filter to parent component
 * - "Clear Filters" button to reset all filters/sorts to defaults
 * - Responsive mobile/desktop layout
 */

"use client";

import React from "react";
import { Button } from "./ui/Button";

export type FilterStatus = "all" | "pending" | "completed" | "overdue";

export interface TaskFiltersProps {
  selectedFilter: FilterStatus;
  onFilterChange: (filter: FilterStatus) => void;
  onClearFilters?: () => void;
  canClearFilters?: boolean;
}

export const TaskFilters: React.FC<TaskFiltersProps> = ({
  selectedFilter,
  onFilterChange,
  onClearFilters,
  canClearFilters = false,
}) => {
  const filters: Array<{ value: FilterStatus; label: string; icon: React.ReactElement }> = [
    {
      value: "all",
      label: "All",
      icon: (
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
      ),
    },
    {
      value: "pending",
      label: "Pending",
      icon: (
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
    },
    {
      value: "completed",
      label: "Completed",
      icon: (
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
    },
    {
      value: "overdue",
      label: "Overdue",
      icon: (
        <svg
          className="w-4 h-4"
          fill="currentColor"
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <path
            fillRule="evenodd"
            d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
            clipRule="evenodd"
          />
        </svg>
      ),
    },
  ];

  return (
    <div className="flex flex-col sm:flex-row sm:items-center gap-3 mb-6">
      {/* Filter button group */}
      <div className="inline-flex flex-wrap sm:flex-nowrap gap-2" role="group" aria-label="Task filters">
        {filters.map((filter) => {
          const isActive = selectedFilter === filter.value;
          return (
            <button
              key={filter.value}
              onClick={() => onFilterChange(filter.value)}
              className={`
                inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg
                transition-all duration-200 ease-in-out
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                ${
                  isActive
                    ? "bg-blue-600 text-white shadow-md hover:bg-blue-700"
                    : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 hover:border-gray-400"
                }
              `}
              aria-pressed={isActive}
              aria-label={`Filter by ${filter.label}`}
            >
              {filter.icon}
              <span className="whitespace-nowrap">{filter.label}</span>
            </button>
          );
        })}
      </div>

      {/* Clear filters button */}
      {onClearFilters && (
        <button
          onClick={onClearFilters}
          disabled={!canClearFilters}
          className={`
            inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg
            transition-all duration-200 ease-in-out
            focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2
            ${
              canClearFilters
                ? "bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 hover:border-gray-400 cursor-pointer"
                : "bg-gray-50 text-gray-400 border border-gray-200 cursor-not-allowed opacity-60"
            }
          `}
          aria-label="Clear all filters and sorting"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
          <span className="whitespace-nowrap">Clear Filters</span>
        </button>
      )}
    </div>
  );
};
