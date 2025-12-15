/**
 * Task Sort Component (T085)
 *
 * Features:
 * - Dropdown menu with sort options: Due Date, Priority, Status, Created Date
 * - Order selector: Ascending, Descending
 * - Display current sort selection
 * - Responsive design
 */

"use client";

import React, { useState, useRef, useEffect } from "react";

export type SortField = "due_date" | "priority" | "status" | "created_at";
export type SortOrder = "asc" | "desc";

export interface TaskSortProps {
  sortBy: SortField;
  order: SortOrder;
  onSortChange: (sortBy: SortField, order: SortOrder) => void;
}

interface SortOption {
  value: SortField;
  label: string;
}

const sortOptions: SortOption[] = [
  { value: "created_at", label: "Created Date" },
  { value: "due_date", label: "Due Date" },
  { value: "priority", label: "Priority" },
  { value: "status", label: "Status" },
];

export const TaskSort: React.FC<TaskSortProps> = ({
  sortBy,
  order,
  onSortChange,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const currentSortLabel =
    sortOptions.find((opt) => opt.value === sortBy)?.label || "Created Date";
  const orderLabel = order === "asc" ? "Ascending" : "Descending";

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleSortByChange = (newSortBy: SortField) => {
    onSortChange(newSortBy, order);
    setIsOpen(false);
  };

  const handleOrderToggle = () => {
    const newOrder: SortOrder = order === "asc" ? "desc" : "asc";
    onSortChange(sortBy, newOrder);
  };

  return (
    <div className="flex flex-col sm:flex-row gap-2 items-stretch sm:items-center">
      {/* Sort by dropdown */}
      <div className="relative" ref={dropdownRef}>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full sm:w-auto inline-flex items-center justify-between gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200"
          aria-label="Sort tasks by"
          aria-expanded={isOpen}
          aria-haspopup="true"
        >
          <svg
            className="w-4 h-4 text-gray-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"
            />
          </svg>
          <span className="whitespace-nowrap">Sort by: {currentSortLabel}</span>
          <svg
            className={`w-4 h-4 text-gray-500 transition-transform duration-200 ${
              isOpen ? "rotate-180" : ""
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>

        {/* Dropdown menu */}
        {isOpen && (
          <div
            className="absolute z-10 mt-2 w-full sm:w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1"
            role="menu"
            aria-orientation="vertical"
            aria-labelledby="sort-menu"
          >
            {sortOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => handleSortByChange(option.value)}
                className={`
                  w-full text-left px-4 py-2 text-sm transition-colors
                  ${
                    sortBy === option.value
                      ? "bg-blue-50 text-blue-700 font-medium"
                      : "text-gray-700 hover:bg-gray-50"
                  }
                `}
                role="menuitem"
                aria-label={`Sort by ${option.label}`}
              >
                <div className="flex items-center justify-between">
                  <span>{option.label}</span>
                  {sortBy === option.value && (
                    <svg
                      className="w-4 h-4 text-blue-600"
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
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Order toggle button */}
      <button
        onClick={handleOrderToggle}
        className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200"
        aria-label={`Change sort order to ${
          order === "asc" ? "descending" : "ascending"
        }`}
      >
        {order === "asc" ? (
          <svg
            className="w-4 h-4 text-gray-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4"
            />
          </svg>
        ) : (
          <svg
            className="w-4 h-4 text-gray-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"
            />
          </svg>
        )}
        <span className="whitespace-nowrap">{orderLabel}</span>
      </button>
    </div>
  );
};
