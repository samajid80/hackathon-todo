/**
 * Task List Page (T056, T057, T060, T064, T066, T084, T086, T089, T110-T115, T128-T134, T143, T151)
 *
 * Features:
 * - Display all user's tasks
 * - Show empty state message when no tasks
 * - "Create Task" button to navigate to /tasks/new
 * - Loading state while fetching tasks
 * - Error handling with retry option
 * - Use useEffect to fetch tasks on page load
 * - Display each task with title, priority, status, due date, created date
 * - Order by created_at DESC (newest first)
 * - Click on task to view details
 * - Show task count
 * - Responsive layout switching (mobile cards, desktop table)
 * - Display success toast after task creation
 * - Display success toast after task update
 * - Filter tasks by status (All, Pending, Completed, Overdue) (T084)
 * - Sort tasks by field and order (T086)
 * - Maintain filter when changing sort and vice versa
 * - Display appropriate empty state messages based on filters (T089)
 * - Mark Complete functionality with optimistic updates (T110-T115)
 * - Delete functionality with confirmation dialog (T128-T134)
 * - Error handling for mark complete with toast notifications
 * - Error-aware empty states (401, 403, 404, network errors) (T143)
 * - Pagination with "Load More" button (T151)
 */

"use client";

import React, { useEffect, useState, useRef, useCallback, Suspense } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getTasks, deleteTask } from "@/lib/api/tasks";
import { ApiError } from "@/lib/api/tasks";
import { Task } from "@/types/task";
import { TaskCard } from "@/components/TaskCard";
import { TaskTable } from "@/components/TaskTable";
import { TaskFilters, FilterStatus } from "@/components/TaskFilters";
import { TaskSort, SortField, SortOrder } from "@/components/TaskSort";
import { Button } from "@/components/ui/Button";
import { useToast } from "@/lib/toast-context";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { SuccessToast } from "@/components/alerts/SuccessToast";

export default function TasksPage() {
  const router = useRouter();
  const toast = useToast();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<{
    message: string;
    statusCode: number;
    isNetworkError: boolean;
  } | null>(null);

  // T151: Pagination state
  const [totalTasks, setTotalTasks] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const TASKS_PER_PAGE = 20;

  // Delete confirmation dialog state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<Task | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Filter and sort state
  const [filterStatus, setFilterStatus] = useState<FilterStatus>("all");
  const [sortBy, setSortBy] = useState<SortField>("created_at");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");

  // Ref to track current task count for pagination
  const tasksCountRef = useRef(0);

  const fetchTasks = useCallback(async (append = false) => {
    try {
      if (!append) {
        setIsLoading(true);
        setError(null);
      } else {
        setIsLoadingMore(true);
      }

      // Build filter and sort parameters
      const filter =
        filterStatus !== "all" ? { status: filterStatus } : undefined;
      const sort = { sortBy, order: sortOrder };

      // T151: Calculate pagination skip based on current tasks
      // Use ref to get current task count
      const skip = append ? tasksCountRef.current : 0;
      const pagination = { skip, limit: TASKS_PER_PAGE };

      const data = await getTasks(filter, sort, pagination);

      // T151: Handle paginated response
      if (append) {
        setTasks((prevTasks) => {
          const newTasks = [...prevTasks, ...data.items];
          tasksCountRef.current = newTasks.length;
          return newTasks;
        });
      } else {
        setTasks(data.items);
        tasksCountRef.current = data.items.length;
      }

      setTotalTasks(data.total);
      setHasMore(data.has_more);
    } catch (err) {
      let errorMessage = "Failed to load tasks";
      let statusCode = 500;
      let isNetworkError = false;

      if (err instanceof ApiError) {
        errorMessage = err.message;
        statusCode = err.statusCode;
        isNetworkError = err.isNetworkError;
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }

      setError({ message: errorMessage, statusCode, isNetworkError });
    } finally {
      setIsLoading(false);
      setIsLoadingMore(false);
    }
  }, [filterStatus, sortBy, sortOrder]);

  // T151: Load more tasks
  const loadMoreTasks = () => {
    fetchTasks(true);
  };

  // Separate effect for fetching tasks
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleEdit = (taskId: string) => {
    router.push(`/tasks/${taskId}/edit`);
  };

  /**
   * T129: Handle delete button click - show confirmation dialog
   */
  const handleDeleteClick = (taskId: string) => {
    const task = tasks.find((t) => t.id === taskId);
    if (task) {
      setTaskToDelete(task);
      setDeleteDialogOpen(true);
    }
  };

  /**
   * T131: Handle delete cancellation - close dialog
   */
  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setTaskToDelete(null);
  };

  /**
   * T130, T132, T133, T134: Handle delete confirmation
   * - Call API on confirm
   * - Optimistic update (remove from UI)
   * - Show success toast
   * - Handle errors (403, 404, network errors)
   */
  const handleDeleteConfirm = async () => {
    if (!taskToDelete) return;

    setIsDeleting(true);
    const taskId = taskToDelete.id;
    const taskTitle = taskToDelete.title;

    // T132: Optimistic update - remove task from UI immediately
    const previousTasks = [...tasks];
    setTasks((prevTasks) => {
      const newTasks = prevTasks.filter((task) => task.id !== taskId);
      tasksCountRef.current = newTasks.length;
      return newTasks;
    });
    setTotalTasks((prev) => prev - 1);

    // Close dialog immediately
    setDeleteDialogOpen(false);

    try {
      // T130: Call API to delete task
      await deleteTask(taskId);

      // T133: Show success message
      toast.success(`Task "${taskTitle}" deleted successfully`);
    } catch (err) {
      // T132: Revert optimistic update on error
      setTasks(previousTasks);
      tasksCountRef.current = previousTasks.length;
      setTotalTasks((prev) => prev + 1);

      // T134: Handle 403 Forbidden and 404 Not Found errors
      let errorMessage = "Failed to delete task";
      if (err instanceof ApiError) {
        if (err.statusCode === 403) {
          errorMessage = "You don't have permission to delete this task";
        } else if (err.statusCode === 404) {
          errorMessage = "Task not found or already deleted";
        } else {
          errorMessage = err.message;
        }
      }

      toast.error(errorMessage);
    } finally {
      setIsDeleting(false);
      setTaskToDelete(null);
    }
  };

  const handleComplete = (taskId: string) => {
    // Update the task in the local state
    setTasks((prevTasks) => {
      const newTasks = prevTasks.map((task) =>
        task.id === taskId ? { ...task, status: "completed" as const } : task
      );
      tasksCountRef.current = newTasks.length;
      return newTasks;
    });
    toast.success("Task marked as complete!");
  };

  const handleError = (message: string) => {
    toast.error(message);
  };

  const handleFilterChange = (newFilter: FilterStatus) => {
    setFilterStatus(newFilter);
  };

  const handleSortChange = (newSortBy: SortField, newOrder: SortOrder) => {
    setSortBy(newSortBy);
    setSortOrder(newOrder);
  };

  const handleClearFilters = () => {
    setFilterStatus("all");
    setSortBy("created_at");
    setSortOrder("desc");
  };

  const isFiltersActive = () => {
    return filterStatus !== "all" || sortBy !== "created_at" || sortOrder !== "desc";
  };

  // Get empty state message based on filter
  const getEmptyStateMessage = () => {
    if (filterStatus === "completed") {
      return {
        title: "No completed tasks yet",
        message: "Complete some tasks to see them here!",
      };
    } else if (filterStatus === "overdue") {
      return {
        title: "No overdue tasks",
        message: "No overdue tasks! You're on track.",
      };
    } else if (filterStatus === "pending") {
      return {
        title: "No pending tasks",
        message: "No pending tasks. Great job!",
      };
    } else {
      return {
        title: "No tasks yet",
        message: "No tasks yet. Create your first task!",
      };
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <svg
            className="animate-spin h-10 w-10 text-blue-600 mx-auto mb-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <p className="text-gray-600">Loading tasks...</p>
        </div>
      </div>
    );
  }

  // T143: Error-aware error states
  if (error) {
    // Network error
    if (error.isNetworkError) {
      return (
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center max-w-md">
            <svg
              className="h-12 w-12 text-orange-600 mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414"
              />
            </svg>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              No Internet Connection
            </h2>
            <p className="text-gray-600 mb-4">
              Unable to connect to server. Please check your internet connection and try again.
            </p>
            <Button onClick={() => fetchTasks()}>Retry</Button>
          </div>
        </div>
      );
    }

    // T143: 401 Unauthorized - Session expired
    if (error.statusCode === 401) {
      return (
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center max-w-md">
            <svg
              className="h-12 w-12 text-yellow-600 mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Session Expired
            </h2>
            <p className="text-gray-600 mb-4">
              Your session has expired. Please log in again to continue.
            </p>
            <Button onClick={() => router.push("/login")}>Log In</Button>
          </div>
        </div>
      );
    }

    // T143: 403 Forbidden - No permission
    if (error.statusCode === 403) {
      return (
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center max-w-md">
            <svg
              className="h-12 w-12 text-red-600 mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
              />
            </svg>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Access Denied
            </h2>
            <p className="text-gray-600 mb-4">
              You don't have permission to view this page.
            </p>
            <Button onClick={() => router.push("/")}>Go Home</Button>
          </div>
        </div>
      );
    }

    // Generic error state with retry
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center max-w-md">
          <svg
            className="h-12 w-12 text-red-600 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Failed to Load Tasks
          </h2>
          <p className="text-gray-600 mb-4">{error.message}</p>
          <Button onClick={() => fetchTasks()}>Retry</Button>
        </div>
      </div>
    );
  }

  // T143: Empty state (after successful load)
  if (tasks.length === 0) {
    const emptyState = getEmptyStateMessage();
    return (
      <div>
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900">My Tasks</h1>
          <Link href="/tasks/new">
            <Button>
              Create Task
            </Button>
          </Link>
        </div>

        {/* Filters and Sort */}
        <div className="mb-6 flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
          <TaskFilters
            selectedFilter={filterStatus}
            onFilterChange={handleFilterChange}
            onClearFilters={handleClearFilters}
            canClearFilters={isFiltersActive()}
          />
          <TaskSort
            sortBy={sortBy}
            order={sortOrder}
            onSortChange={handleSortChange}
          />
        </div>

        {/* Empty state */}
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <svg
              className="h-24 w-24 text-gray-400 mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              {emptyState.title}
            </h2>
            <p className="text-gray-600 mb-6">{emptyState.message}</p>
            <Link href="/tasks/new">
              <Button>
                Create Your First Task
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Tasks list
  return (
    <div>
      {/* Success toast notifications with Suspense boundaries */}
      <Suspense fallback={null}>
        <SuccessToast
          paramName="created"
          message="Task created successfully!"
          onShow={toast.success}
          onDetected={fetchTasks}
        />
      </Suspense>

      <Suspense fallback={null}>
        <SuccessToast
          paramName="updated"
          message="Task updated successfully!"
          onShow={toast.success}
          onDetected={fetchTasks}
        />
      </Suspense>

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Tasks</h1>
          <p className="text-gray-600 mt-1">
            Showing {tasks.length} of {totalTasks} {totalTasks === 1 ? "task" : "tasks"}
          </p>
        </div>
        <Link href="/tasks/new">
          <Button>
            <span className="hidden sm:inline">Create Task</span>
            <span className="sm:hidden">New</span>
          </Button>
        </Link>
      </div>

      {/* Filters and Sort */}
      <div className="mb-6 flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
        <TaskFilters
          selectedFilter={filterStatus}
          onFilterChange={handleFilterChange}
          onClearFilters={handleClearFilters}
          canClearFilters={isFiltersActive()}
        />
        <TaskSort
          sortBy={sortBy}
          order={sortOrder}
          onSortChange={handleSortChange}
        />
      </div>

      {/* Mobile view: Task cards (T060) */}
      <div className="md:hidden space-y-4">
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onEdit={handleEdit}
            onDelete={handleDeleteClick}
            onComplete={handleComplete}
            onError={handleError}
          />
        ))}
      </div>

      {/* Desktop view: Task table (T060) */}
      <div className="hidden md:block">
        <TaskTable
          tasks={tasks}
          onEdit={handleEdit}
          onDelete={handleDeleteClick}
          onComplete={handleComplete}
          onError={handleError}
        />
      </div>

      {/* T151: Load More button */}
      {hasMore && (
        <div className="mt-8 flex justify-center">
          <Button
            onClick={loadMoreTasks}
            disabled={isLoadingMore}
            variant="secondary"
          >
            {isLoadingMore ? (
              <>
                <svg
                  className="animate-spin h-5 w-5 mr-2"
                  xmlns="http://www.w3.org/2000/svg"
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
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Loading...
              </>
            ) : (
              <>
                Load More
                <svg
                  className="w-5 h-5 ml-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </>
            )}
          </Button>
        </div>
      )}

      {/* T128: Confirmation dialog for delete action */}
      <ConfirmDialog
        isOpen={deleteDialogOpen}
        title="Delete Task"
        message={`Are you sure you want to delete "${taskToDelete?.title}"? This action cannot be undone.`}
        confirmLabel="Delete"
        cancelLabel="Cancel"
        variant="danger"
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />
    </div>
  );
}
