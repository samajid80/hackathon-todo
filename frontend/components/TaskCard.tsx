/**
 * Task Card Component (T058, T087, T109-T115)
 *
 * Features:
 * - Mobile-friendly card layout
 * - Display: title, priority, status, due date
 * - Clickable to view details
 * - Priority color coding (low=gray, medium=blue, high=red)
 * - Status indicator (checkmark for completed)
 * - Show creation date
 * - Overdue indicator (red border and badge) if due_date < today and status = pending
 * - Edit button (links to edit page)
 * - Delete button
 * - Mark Complete button (only for pending tasks)
 * - Visual distinction for completed tasks (strikethrough, green, faded)
 * - Optimistic UI updates for complete action
 * - Loading states during API calls
 */

"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Task, formatDueDate, isTaskOverdue } from "@/types/task";
import { PriorityBadge } from "./PriorityBadge";
import { StatusBadge } from "./StatusBadge";
import { Button } from "./ui/Button";
import { completeTask } from "@/lib/api/tasks";
import { ApiError } from "@/lib/api/tasks";

export interface TaskCardProps {
  task: Task;
  onEdit?: (taskId: string) => void;
  onDelete?: (taskId: string) => void;
  onComplete?: (taskId: string) => void;
  onError?: (message: string) => void;
}

export const TaskCard: React.FC<TaskCardProps> = ({
  task: initialTask,
  onEdit,
  onDelete,
  onComplete,
  onError,
}) => {
  const router = useRouter();
  const [task, setTask] = useState(initialTask);
  const [isCompleting, setIsCompleting] = useState(false);
  const isOverdue = isTaskOverdue(task);
  const isCompleted = task.status === "completed";
  const isPending = task.status === "pending";

  const formatCreatedDate = (dateString: string): string => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    }).format(date);
  };

  const handleComplete = async () => {
    if (isCompleting) return;

    setIsCompleting(true);

    // Optimistic update
    const previousTask = { ...task };
    setTask({ ...task, status: "completed" });

    try {
      const updatedTask = await completeTask(task.id);
      setTask(updatedTask);
      if (onComplete) {
        onComplete(task.id);
      }
    } catch (err) {
      // Revert optimistic update on error
      setTask(previousTask);

      let errorMessage = "Failed to mark task as complete";
      if (err instanceof ApiError) {
        if (err.statusCode === 403) {
          errorMessage = "You don't have permission to complete this task";
        } else if (err.statusCode === 404) {
          errorMessage = "Task not found or has been deleted";
        } else {
          errorMessage = err.message;
        }
      }

      if (onError) {
        onError(errorMessage);
      }
    } finally {
      setIsCompleting(false);
    }
  };

  const handleEditClick = () => {
    if (onEdit) {
      onEdit(task.id);
    } else {
      router.push(`/tasks/${task.id}/edit`);
    }
  };

  return (
    <div
      className={`
        bg-white rounded-lg shadow-sm p-4 hover:shadow-md transition-all duration-200
        ${isOverdue && !isCompleted ? "border-2 border-red-500" : "border border-gray-200"}
        ${isCompleted ? "opacity-75 bg-green-50" : ""}
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <Link
          href={`/tasks/${task.id}`}
          className="flex-1 min-w-0 group focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
        >
          <h3
            className={`text-lg font-semibold group-hover:text-blue-600 transition-colors truncate ${
              isCompleted
                ? "line-through text-gray-500"
                : "text-gray-900"
            }`}
          >
            {task.title}
          </h3>
        </Link>
        {isCompleted && (
          <svg
            className="w-6 h-6 text-green-600 flex-shrink-0 ml-2"
            fill="currentColor"
            viewBox="0 0 20 20"
            aria-hidden="true"
            aria-label="Completed"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
        )}
      </div>

      {/* Description preview */}
      {task.description && (
        <p
          className={`text-sm mb-3 line-clamp-2 ${
            isCompleted ? "text-gray-500" : "text-gray-600"
          }`}
        >
          {task.description}
        </p>
      )}

      {/* Badges */}
      <div className="flex flex-wrap gap-2 mb-3">
        <StatusBadge status={task.status} />
        <PriorityBadge priority={task.priority} />
        {isOverdue && !isCompleted && (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <svg
              className="w-3 h-3"
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
            Overdue
          </span>
        )}
      </div>

      {/* Dates */}
      <div className="text-xs text-gray-500 mb-3 space-y-1">
        <div className="flex items-center gap-1">
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
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          <span className={isOverdue && !isCompleted ? "text-red-600 font-medium" : ""}>
            Due: {formatDueDate(task.due_date)}
          </span>
        </div>
        <div className="flex items-center gap-1">
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
          <span>Created: {formatCreatedDate(task.created_at)}</span>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2 pt-3 border-t border-gray-100">
        {/* Mark Complete button - only for pending tasks */}
        {isPending && (
          <Button
            onClick={handleComplete}
            disabled={isCompleting}
            isLoading={isCompleting}
            variant="primary"
            className="flex-1 text-sm py-1.5"
            aria-label="Mark task as complete"
          >
            {!isCompleting && (
              <svg
                className="w-4 h-4 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            )}
            {isCompleting ? "Completing..." : "Complete"}
          </Button>
        )}

        {/* Edit button - only for pending tasks */}
        {isPending && onEdit && (
          <Button
            variant="secondary"
            onClick={handleEditClick}
            disabled={isCompleting}
            className="flex-1 text-sm py-1.5"
          >
            <svg
              className="w-4 h-4 mr-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
            Edit
          </Button>
        )}

        {/* Delete button */}
        {onDelete && (
          <Button
            variant="danger"
            onClick={() => onDelete(task.id)}
            disabled={isCompleting}
            className="flex-1 text-sm py-1.5"
          >
            <svg
              className="w-4 h-4 mr-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
            Delete
          </Button>
        )}
      </div>
    </div>
  );
};
