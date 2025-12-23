/**
 * Task data types for the frontend application
 */

export type Status = "pending" | "completed";
export type Priority = "low" | "medium" | "high";

/**
 * Task object returned by the API
 */
export interface Task {
  id: string;
  title: string;
  description: string | null;
  due_date: string | null; // ISO 8601 date string (YYYY-MM-DD)
  priority: Priority;
  status: Status;
  tags: string[]; // Task category labels (max 10, lowercase alphanumeric + hyphens)
  user_id: string;
  created_at: string; // ISO 8601 datetime string
  updated_at: string; // ISO 8601 datetime string
}

/**
 * Task creation data
 */
export interface TaskCreate {
  title: string;
  description?: string | null;
  due_date?: string | null; // ISO 8601 date string (YYYY-MM-DD)
  priority?: Priority;
  status?: Status;
  tags?: string[]; // Task category labels (max 10, lowercase alphanumeric + hyphens)
}

/**
 * Task update data (all fields optional for partial updates)
 */
export interface TaskUpdate {
  title?: string;
  description?: string | null;
  due_date?: string | null; // ISO 8601 date string (YYYY-MM-DD)
  priority?: Priority;
  status?: Status;
  tags?: string[]; // Task category labels (max 10, lowercase alphanumeric + hyphens)
}

/**
 * Task filter options (T084)
 */
export type FilterStatus = "all" | "pending" | "completed" | "overdue";

export interface TaskFilter {
  status?: FilterStatus;
  tags?: string[]; // Filter by tags (AND logic - task must have ALL specified tags)
}

/**
 * Task sort options (T086)
 */
export type SortField = "due_date" | "priority" | "status" | "created_at";
export type SortOrder = "asc" | "desc";

export interface TaskSort {
  sortBy: SortField;
  order: SortOrder;
}

/**
 * Pagination options (T151)
 */
export interface PaginationOptions {
  skip?: number;
  limit?: number;
}

/**
 * Paginated response from the API (T151)
 */
export interface PaginatedTasksResponse {
  items: Task[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

/**
 * Format due date for display
 * @param due_date ISO 8601 date string or null
 * @returns Formatted date string or "No due date"
 */
export function formatDueDate(due_date: string | null): string {
  if (!due_date) {
    return "No due date";
  }

  const date = new Date(due_date);
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

/**
 * Check if a task is overdue
 * @param task Task object
 * @returns true if task is pending and due date is in the past
 */
export function isTaskOverdue(task: Task): boolean {
  if (!task.due_date || task.status !== "pending") {
    return false;
  }

  const today = new Date();
  today.setHours(0, 0, 0, 0); // Reset to start of day

  const dueDate = new Date(task.due_date);
  dueDate.setHours(0, 0, 0, 0); // Reset to start of day

  return dueDate < today;
}

/**
 * Get display label for priority
 * @param priority Priority value
 * @returns Capitalized priority label
 */
export function getPriorityLabel(priority: Priority): string {
  return priority.charAt(0).toUpperCase() + priority.slice(1);
}

/**
 * Get display label for status
 * @param status Status value
 * @returns Capitalized status label
 */
export function getStatusLabel(status: Status): string {
  return status.charAt(0).toUpperCase() + status.slice(1);
}
