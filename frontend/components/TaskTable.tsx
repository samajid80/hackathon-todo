/**
 * Task Table Component (T059, T087, T109-T115)
 *
 * Features:
 * - Desktop-friendly table layout
 * - Columns: Title, Priority, Status, Due Date, Actions
 * - Sortable column headers
 * - Priority color coding
 * - Status badges
 * - Overdue indicator (red border) for overdue task rows
 * - Edit button (links to edit page)
 * - Delete button
 * - Mark Complete button (only for pending tasks)
 * - Visual distinction for completed tasks (strikethrough, green row tint, faded)
 * - Optimistic UI updates for complete action
 * - Loading states during API calls
 * - Hover effects for better UX
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

export interface TaskTableProps {
  tasks: Task[];
  onEdit?: (taskId: string) => void;
  onDelete?: (taskId: string) => void;
  onComplete?: (taskId: string) => void;
  onError?: (message: string) => void;
}

export const TaskTable: React.FC<TaskTableProps> = ({
  tasks: initialTasks,
  onEdit,
  onDelete,
  onComplete,
  onError,
}) => {
  const router = useRouter();
  const [tasks, setTasks] = useState(initialTasks);
  const [completingTasks, setCompletingTasks] = useState<Set<string>>(new Set());

  // Update tasks when prop changes
  React.useEffect(() => {
    setTasks(initialTasks);
  }, [initialTasks]);

  const handleComplete = async (taskId: string) => {
    if (completingTasks.has(taskId)) return;

    // Add to completing set
    setCompletingTasks(prev => new Set(prev).add(taskId));

    // Optimistic update
    const previousTasks = [...tasks];
    setTasks(tasks.map(task =>
      task.id === taskId ? { ...task, status: "completed" as const } : task
    ));

    try {
      const updatedTask = await completeTask(taskId);
      setTasks(tasks.map(task =>
        task.id === taskId ? updatedTask : task
      ));
      if (onComplete) {
        onComplete(taskId);
      }
    } catch (err) {
      // Revert optimistic update on error
      setTasks(previousTasks);

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
      // Remove from completing set
      setCompletingTasks(prev => {
        const next = new Set(prev);
        next.delete(taskId);
        return next;
      });
    }
  };

  const handleEditClick = (taskId: string) => {
    if (onEdit) {
      onEdit(taskId);
    } else {
      router.push(`/tasks/${taskId}/edit`);
    }
  };


  const formatCreatedDate = (dateString: string): string => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    }).format(date);
  };

  return (
    <div className="overflow-x-auto border border-gray-200 rounded-lg">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Title
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Priority
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Status
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Due Date
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Created
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {tasks.map((task) => {
            const isOverdue = isTaskOverdue(task);
            const isCompleted = task.status === "completed";
            const isPending = task.status === "pending";
            const isCompleting = completingTasks.has(task.id);

            return (
              <tr
                key={task.id}
                className={`
                  hover:bg-gray-50 transition-all duration-200
                  ${isOverdue && !isCompleted ? "border-l-4 border-l-red-500 bg-red-50" : ""}
                  ${isCompleted ? "bg-green-50 opacity-75" : ""}
                `}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-2">
                    {isCompleted && (
                      <svg
                        className="w-5 h-5 text-green-600 flex-shrink-0"
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
                    <Link
                      href={`/tasks/${task.id}`}
                      className={`text-sm font-medium hover:text-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded ${
                        isCompleted
                          ? "line-through text-gray-500"
                          : "text-gray-900"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        {task.title}
                        {isOverdue && !isCompleted && (
                          <svg
                            className="w-4 h-4 text-red-600"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                            aria-hidden="true"
                            aria-label="Overdue"
                          >
                            <path
                              fillRule="evenodd"
                              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                              clipRule="evenodd"
                            />
                          </svg>
                        )}
                      </div>
                    </Link>
                  </div>
                  {task.description && (
                    <p
                      className={`text-sm truncate max-w-md mt-1 ${
                        isCompleted ? "text-gray-500" : "text-gray-500"
                      }`}
                    >
                      {task.description}
                    </p>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <PriorityBadge priority={task.priority} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <StatusBadge status={task.status} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`text-sm ${
                      isOverdue && !isCompleted
                        ? "text-red-600 font-medium"
                        : isCompleted
                        ? "text-gray-500"
                        : "text-gray-900"
                    }`}
                  >
                    {formatDueDate(task.due_date)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatCreatedDate(task.created_at)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex justify-end gap-2">
                    {/* Mark Complete button - only for pending tasks */}
                    {isPending && (
                      <Button
                        onClick={() => handleComplete(task.id)}
                        disabled={isCompleting}
                        isLoading={isCompleting}
                        variant="primary"
                        className="text-xs py-1 px-2"
                        aria-label={`Mark ${task.title} as complete`}
                        title="Mark as complete"
                      >
                        {!isCompleting && (
                          <svg
                            className="w-3 h-3"
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
                      </Button>
                    )}

                    {/* Edit button - only for pending tasks */}
                    {isPending && onEdit && (
                      <Button
                        variant="secondary"
                        onClick={() => handleEditClick(task.id)}
                        disabled={isCompleting}
                        className="text-xs py-1 px-2"
                        aria-label={`Edit ${task.title}`}
                        title="Edit task"
                      >
                        <svg
                          className="w-3 h-3"
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
                      </Button>
                    )}

                    {/* Delete button */}
                    {onDelete && (
                      <Button
                        variant="danger"
                        onClick={() => onDelete(task.id)}
                        disabled={isCompleting}
                        className="text-xs py-1 px-2"
                        aria-label={`Delete ${task.title}`}
                        title="Delete task"
                      >
                        <svg
                          className="w-3 h-3"
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
                      </Button>
                    )}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
