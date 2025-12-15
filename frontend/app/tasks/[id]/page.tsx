/**
 * Task Detail View Page
 *
 * Features:
 * - Read-only display of task details
 * - Status and priority badges
 * - Due date and timestamps
 * - Action buttons: Edit, Mark Complete, Delete
 * - Loading state while fetching task
 * - Error states for 404, 403, and network errors
 * - Confirmation dialog for delete action
 * - Responsive layout
 */

"use client";

import React, { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { getTask, completeTask, deleteTask } from "@/lib/api/tasks";
import { Task } from "@/types/task";
import { Button } from "@/components/ui/Button";
import { StatusBadge } from "@/components/StatusBadge";
import { PriorityBadge } from "@/components/PriorityBadge";
import { ApiError } from "@/lib/api/tasks";

export default function TaskDetailPage() {
  const router = useRouter();
  const params = useParams();
  const taskId = params.id as string;

  const [isLoading, setIsLoading] = useState(true);
  const [task, setTask] = useState<Task | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [accessDenied, setAccessDenied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isCompleting, setIsCompleting] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Fetch task data on mount
  useEffect(() => {
    const fetchTask = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const fetchedTask = await getTask(taskId);
        setTask(fetchedTask);
      } catch (err) {
        if (err instanceof ApiError) {
          if (err.statusCode === 404) {
            setNotFound(true);
          } else if (err.statusCode === 403) {
            setAccessDenied(true);
          } else {
            setError(err.message);
          }
        } else {
          setError("Failed to load task. Please try again.");
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchTask();
  }, [taskId]);

  // Handle mark as complete
  const handleComplete = async () => {
    if (!task) return;

    try {
      setIsCompleting(true);
      setError(null);
      const updatedTask = await completeTask(taskId);
      setTask(updatedTask);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to mark task as complete. Please try again.");
      }
    } finally {
      setIsCompleting(false);
    }
  };

  // Handle delete
  const handleDelete = async () => {
    try {
      setIsDeleting(true);
      setError(null);
      await deleteTask(taskId);
      router.push("/tasks");
    } catch (err) {
      setIsDeleting(false);
      setShowDeleteConfirm(false);
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to delete task. Please try again.");
      }
    }
  };

  // Format date for display
  const formatDate = (dateString: string | null): string => {
    if (!dateString) return "Not set";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  // Format datetime for display
  const formatDateTime = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="animate-pulse">
              <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 404 Not Found state
  if (notFound) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Task Not Found
            </h1>
            <p className="text-gray-600 mb-6">
              The task you're looking for doesn't exist or has been deleted.
            </p>
            <Link href="/tasks">
              <Button variant="primary">Back to Tasks</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // 403 Access Denied state
  if (accessDenied) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Access Denied
            </h1>
            <p className="text-gray-600 mb-6">
              You don't have permission to view this task.
            </p>
            <Link href="/tasks">
              <Button variant="primary">Back to Tasks</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Task not loaded (general error)
  if (!task) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Error Loading Task
            </h1>
            <p className="text-red-600 mb-6">
              {error || "An unexpected error occurred."}
            </p>
            <Link href="/tasks">
              <Button variant="primary">Back to Tasks</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const isCompleted = task.status === "completed";

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6">
          <Link
            href="/tasks"
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4"
          >
            <svg
              className="w-4 h-4 mr-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Back to Tasks
          </Link>
        </div>

        {/* Error message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Task Detail Card */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {/* Task Header */}
          <div className="px-6 py-5 border-b border-gray-200">
            <div className="flex items-start justify-between mb-3">
              <h1 className="text-2xl font-bold text-gray-900 flex-1">
                {task.title}
              </h1>
              <div className="flex gap-2 ml-4">
                <StatusBadge status={task.status} />
                <PriorityBadge priority={task.priority} />
              </div>
            </div>
          </div>

          {/* Task Body */}
          <div className="px-6 py-5">
            {/* Description */}
            <div className="mb-6">
              <h2 className="text-sm font-semibold text-gray-700 mb-2">
                Description
              </h2>
              {task.description ? (
                <p className="text-gray-900 whitespace-pre-wrap">
                  {task.description}
                </p>
              ) : (
                <p className="text-gray-500 italic">No description provided</p>
              )}
            </div>

            {/* Task Metadata */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-6">
              {/* Due Date */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-1">
                  Due Date
                </h3>
                <p className="text-gray-900">{formatDate(task.due_date)}</p>
              </div>

              {/* Created At */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-1">
                  Created
                </h3>
                <p className="text-gray-900">{formatDateTime(task.created_at)}</p>
              </div>

              {/* Updated At */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-1">
                  Last Updated
                </h3>
                <p className="text-gray-900">{formatDateTime(task.updated_at)}</p>
              </div>

              {/* Task ID */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-1">
                  Task ID
                </h3>
                <p className="text-gray-500 text-sm font-mono">{task.id}</p>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex flex-wrap gap-3">
            {!isCompleted && (
              <Link href={`/tasks/${task.id}/edit`}>
                <Button variant="primary">
                  <svg
                    className="w-4 h-4 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                  Edit Task
                </Button>
              </Link>
            )}

            {!isCompleted && (
              <Button
                variant="secondary"
                onClick={handleComplete}
                disabled={isCompleting}
              >
                {isCompleting ? (
                  <>
                    <svg
                      className="animate-spin -ml-1 mr-2 h-4 w-4"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Completing...
                  </>
                ) : (
                  <>
                    <svg
                      className="w-4 h-4 mr-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    Mark Complete
                  </>
                )}
              </Button>
            )}

            <Button
              variant="danger"
              onClick={() => setShowDeleteConfirm(true)}
              disabled={isDeleting}
            >
              <svg
                className="w-4 h-4 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
              Delete Task
            </Button>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Confirm Delete
            </h2>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete this task? This action cannot be
              undone.
            </p>
            <div className="flex gap-3 justify-end">
              <Button
                variant="secondary"
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isDeleting}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={handleDelete}
                disabled={isDeleting}
              >
                {isDeleting ? (
                  <>
                    <svg
                      className="animate-spin -ml-1 mr-2 h-4 w-4"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Deleting...
                  </>
                ) : (
                  "Delete"
                )}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
