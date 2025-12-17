/**
 * API client for task operations (T142 - Enhanced Error Handling, T151 - Pagination)
 *
 * Features:
 * - Type-safe functions for backend API interaction
 * - Automatic JWT authentication headers
 * - Network error detection (no internet connectivity)
 * - Distinction between network errors and API errors (4xx/5xx)
 * - Retry logic for GET requests (max 3 retries with exponential backoff)
 * - Circuit breaker pattern for repeated failures
 * - Pagination support for task list (T151)
 * - Development logging for debugging
 */

import {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskFilter,
  TaskSort,
  PaginationOptions,
  PaginatedTasksResponse,
} from "@/types/task";

/**
 * Get the API base URL from environment variables
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Circuit breaker state
 */
let circuitBreakerFailures = 0;
let circuitBreakerLastFailure = 0;
const CIRCUIT_BREAKER_THRESHOLD = 5;
const CIRCUIT_BREAKER_TIMEOUT = 30000; // 30 seconds

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public details?: unknown,
    public isNetworkError = false
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Check if circuit breaker is open
 */
function isCircuitBreakerOpen(): boolean {
  if (circuitBreakerFailures < CIRCUIT_BREAKER_THRESHOLD) {
    return false;
  }

  const timeSinceLastFailure = Date.now() - circuitBreakerLastFailure;
  if (timeSinceLastFailure > CIRCUIT_BREAKER_TIMEOUT) {
    // Reset circuit breaker after timeout
    circuitBreakerFailures = 0;
    return false;
  }

  return true;
}

/**
 * Record a failure for circuit breaker
 */
function recordFailure(): void {
  circuitBreakerFailures++;
  circuitBreakerLastFailure = Date.now();
}

/**
 * Record a success for circuit breaker
 */
function recordSuccess(): void {
  circuitBreakerFailures = 0;
}

/**
 * Get JWT authentication token from Better-Auth JWT plugin
 * The JWT plugin automatically sets the token in the 'set-auth-jwt' header
 */
async function getAuthToken(): Promise<string | null> {
  if (typeof window === "undefined") {
    console.log("[Auth] getAuthToken: Running on server, no token available");
    return null;
  }

  try {
    // Import authClient dynamically to avoid SSR issues
    const { authClient } = await import("@/lib/auth-client");

    console.log("[Auth] Fetching JWT token from Better-Auth JWT plugin via set-auth-jwt header...");

    // Get session and extract JWT from response header
    // The JWT plugin automatically sets the 'set-auth-jwt' header on authenticated responses
    let jwtToken: string | null = null;

    await authClient.getSession({
      fetchOptions: {
        onSuccess: (ctx) => {
          const token = ctx.response.headers.get("set-auth-jwt");
          if (token) {
            jwtToken = token;
            console.log("[Auth] JWT plugin token received from header (HS256):", token.substring(0, 50) + "...");
          }
        },
      },
    });

    if (!jwtToken) {
      console.error("[Auth] No JWT token found in set-auth-jwt header");
      return null;
    }

    return jwtToken;
  } catch (err) {
    console.error("[Auth] Failed to get JWT plugin token:", err);
    return null;
  }
}

/**
 * Sleep utility for retry delays
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Make an authenticated API request with retry logic (T142)
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  retryCount = 0
): Promise<T> {
  // Check circuit breaker
  if (isCircuitBreakerOpen()) {
    const error = new ApiError(
      "Service temporarily unavailable. Please try again later.",
      503,
      undefined,
      true
    );
    if (process.env.NODE_ENV === "development") {
      console.error("[API] Circuit breaker is open. Too many failures.");
    }
    throw error;
  }

  const token = await getAuthToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  // Merge existing headers
  if (options.headers) {
    const existingHeaders = new Headers(options.headers);
    existingHeaders.forEach((value, key) => {
      headers[key] = value;
    });
  }

  // Add authentication header if token exists
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
    console.log("[API] Request to", endpoint, "with Authorization header");
  } else {
    console.warn("[API] Request to", endpoint, "WITHOUT Authorization header - no token available");
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
      cache: 'no-store', // Disable caching to always get fresh data
    });

    // Record success for circuit breaker
    recordSuccess();

    // Handle different response status codes
    if (!response.ok) {
      let errorMessage = "An error occurred";
      let errorDetails: unknown;

      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
        errorDetails = errorData;
      } catch {
        // If response is not JSON, use status text
        errorMessage = response.statusText;
      }

      // Log API errors in development
      if (process.env.NODE_ENV === "development") {
        console.error(`[API Error] ${response.status} ${endpoint}:`, errorMessage);
      }

      throw new ApiError(errorMessage, response.status, errorDetails, false);
    }

    // Handle 204 No Content (for DELETE operations)
    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  } catch (error) {
    // Check if it's a network error (no internet connectivity)
    if (error instanceof TypeError && error.message.includes("fetch")) {
      const isNetworkError = true;
      recordFailure();

      // Retry GET requests only (idempotent operations)
      const isGetRequest = !options.method || options.method === "GET";
      if (isGetRequest && retryCount < 3) {
        const delay = Math.pow(2, retryCount) * 1000; // Exponential backoff: 1s, 2s, 4s

        if (process.env.NODE_ENV === "development") {
          console.warn(
            `[API] Network error. Retrying in ${delay}ms (attempt ${retryCount + 1}/3)...`
          );
        }

        await sleep(delay);
        return apiRequest<T>(endpoint, options, retryCount + 1);
      }

      // Log network errors in development
      if (process.env.NODE_ENV === "development") {
        console.error("[API] Network error:", error);
      }

      throw new ApiError(
        "Unable to connect to server. Please check your internet connection.",
        0,
        undefined,
        isNetworkError
      );
    }

    // Re-throw ApiError instances
    if (error instanceof ApiError) {
      throw error;
    }

    // Log unknown errors in development
    if (process.env.NODE_ENV === "development") {
      console.error("[API] Unknown error:", error);
    }

    // Unknown error
    throw new ApiError(
      "An unexpected error occurred",
      500,
      error instanceof Error ? error.message : String(error)
    );
  }
}

/**
 * Create a new task
 */
export async function createTask(task: TaskCreate): Promise<Task> {
  return apiRequest<Task>("/api/tasks/", {
    method: "POST",
    body: JSON.stringify(task),
  });
}

/**
 * Get all tasks for the authenticated user with optional filters, sorting, and pagination (T151)
 */
export async function getTasks(
  filter?: TaskFilter,
  sort?: TaskSort,
  pagination?: PaginationOptions
): Promise<PaginatedTasksResponse> {
  const params = new URLSearchParams();

  // Add filter parameters
  if (filter?.status && filter.status !== "all") {
    params.append("status", filter.status);
  }

  // Add sort parameters
  if (sort?.sortBy) {
    params.append("sort_by", sort.sortBy);
  }

  if (sort?.order) {
    params.append("order", sort.order);
  }

  // T151: Add pagination parameters
  if (pagination?.skip !== undefined) {
    params.append("skip", pagination.skip.toString());
  }

  if (pagination?.limit !== undefined) {
    params.append("limit", pagination.limit.toString());
  }

  const query = params.toString();
  const endpoint = query ? `/api/tasks/?${query}` : "/api/tasks/";

  return apiRequest<PaginatedTasksResponse>(endpoint);
}

/**
 * Get a single task by ID
 */
export async function getTask(taskId: string): Promise<Task> {
  return apiRequest<Task>(`/api/tasks/${taskId}`);
}

/**
 * Update a task
 */
export async function updateTask(
  taskId: string,
  update: TaskUpdate
): Promise<Task> {
  return apiRequest<Task>(`/api/tasks/${taskId}`, {
    method: "PUT",
    body: JSON.stringify(update),
  });
}

/**
 * Mark a task as complete
 */
export async function completeTask(taskId: string): Promise<Task> {
  return apiRequest<Task>(`/api/tasks/${taskId}/complete`, {
    method: "PATCH",
  });
}

/**
 * Delete a task
 */
export async function deleteTask(taskId: string): Promise<void> {
  return apiRequest<void>(`/api/tasks/${taskId}`, {
    method: "DELETE",
  });
}
