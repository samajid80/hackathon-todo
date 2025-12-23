/**
 * Task Edit Page (T106, T107, T108)
 *
 * Features:
 * - Pre-filled form with current task data
 * - Form validation (same as create form)
 * - Update submission with redirect
 * - Loading state while fetching task
 * - Error state for 404, 403, validation, and network errors
 * - Title required and max 200 characters
 * - Description max 2000 characters
 * - Priority must be valid enum
 * - Due date must be valid date format
 * - Real-time validation errors
 * - Character count for title/description
 */

"use client";

import React, { useState, useEffect, FormEvent, ChangeEvent, useRef } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { getTask, updateTask } from "@/lib/api/tasks";
import { Task, TaskUpdate, Priority } from "@/types/task";
import { Button } from "@/components/ui/Button";
import { ApiError } from "@/lib/api/tasks";
import { TagSelector, TagSelectorRef } from "@/components/TagSelector";

interface FormErrors {
  title?: string;
  description?: string;
  due_date?: string;
  general?: string;
}

export default function EditTaskPage() {
  const router = useRouter();
  const params = useParams();
  const taskId = params.id as string;
  const tagSelectorRef = useRef<TagSelectorRef>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [task, setTask] = useState<Task | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [accessDenied, setAccessDenied] = useState(false);

  const [formData, setFormData] = useState<TaskUpdate>({
    title: "",
    description: null,
    due_date: null,
    priority: "medium",
    tags: [],
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  // Fetch task data on mount
  useEffect(() => {
    const fetchTask = async () => {
      try {
        setIsLoading(true);
        const fetchedTask = await getTask(taskId);
        setTask(fetchedTask);

        // Pre-fill form with task data
        setFormData({
          title: fetchedTask.title,
          description: fetchedTask.description,
          due_date: fetchedTask.due_date,
          priority: fetchedTask.priority,
          tags: fetchedTask.tags || [],
        });
      } catch (err) {
        if (err instanceof ApiError) {
          if (err.statusCode === 404) {
            setNotFound(true);
          } else if (err.statusCode === 403) {
            setAccessDenied(true);
          } else {
            setErrors({ general: err.message });
          }
        } else {
          setErrors({
            general: "Failed to load task. Please try again.",
          });
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchTask();
  }, [taskId]);

  // Validate a single field
  const validateField = (
    name: keyof TaskUpdate,
    value: string | null | undefined
  ): string | undefined => {
    switch (name) {
      case "title":
        if (!value || value.trim().length === 0) {
          return "Title is required";
        }
        if (value.length > 200) {
          return "Title must be 200 characters or less";
        }
        break;
      case "description":
        if (value && value.length > 2000) {
          return "Description must be 2000 characters or less";
        }
        break;
      case "due_date":
        if (value) {
          const date = new Date(value);
          if (isNaN(date.getTime())) {
            return "Please provide a valid date";
          }
        }
        break;
    }
    return undefined;
  };

  // Handle input change
  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    const processedValue = value === "" || value === null ? null : value;

    setFormData((prev) => ({
      ...prev,
      [name]: processedValue,
    }));

    // Validate if field has been touched
    if (touched[name]) {
      const error = validateField(name as keyof TaskUpdate, processedValue);
      setErrors((prev) => ({
        ...prev,
        [name]: error,
      }));
    }
  };

  // Handle field blur
  const handleBlur = (
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setTouched((prev) => ({ ...prev, [name]: true }));

    const processedValue = value === "" || value === null ? null : value;
    const error = validateField(name as keyof TaskUpdate, processedValue);
    setErrors((prev) => ({
      ...prev,
      [name]: error,
    }));
  };

  // Validate entire form
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    const titleError = validateField("title", formData.title);
    if (titleError) newErrors.title = titleError;

    const descriptionError = validateField(
      "description",
      formData.description ?? null
    );
    if (descriptionError) newErrors.description = descriptionError;

    const dueDateError = validateField("due_date", formData.due_date ?? null);
    if (dueDateError) newErrors.due_date = dueDateError;

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Add any pending tag in the input field before submitting
    if (tagSelectorRef.current) {
      tagSelectorRef.current.addPendingTag();
    }

    // Mark all fields as touched
    setTouched({
      title: true,
      description: true,
      due_date: true,
    });

    // Validate form
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      await updateTask(taskId, formData);
      // Redirect to tasks page with success message
      router.push("/tasks?updated=true");
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.statusCode === 404) {
          setErrors({
            general: "Task not found or has been deleted",
          });
        } else if (err.statusCode === 403) {
          setErrors({
            general: "You don't have permission to edit this task",
          });
        } else if (err.statusCode === 400) {
          // Handle validation errors from backend
          setErrors({
            general: err.message,
          });
        } else {
          setErrors({
            general: err.message,
          });
        }
      } else {
        setErrors({
          general: "Failed to update task. Please try again.",
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Check if form is valid for submit button
  const isFormValid =
    formData.title &&
    formData.title.trim().length > 0 &&
    formData.title.length <= 200 &&
    (!formData.description || formData.description.length <= 2000) &&
    !errors.title &&
    !errors.description &&
    !errors.due_date;

  // Loading state
  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-center py-12">
          <div className="flex items-center gap-3">
            <svg
              className="animate-spin h-8 w-8 text-blue-600"
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
            <span className="text-lg text-gray-600">Loading task...</span>
          </div>
        </div>
      </div>
    );
  }

  // 404 state
  if (notFound) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Task Not Found
          </h2>
          <p className="text-gray-600 mb-6">
            The task you're looking for doesn't exist or has been deleted.
          </p>
          <Link href="/tasks">
            <Button>Back to Tasks</Button>
          </Link>
        </div>
      </div>
    );
  }

  // 403 state
  if (accessDenied) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
          <svg
            className="mx-auto h-12 w-12 text-red-400 mb-4"
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
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Access Denied
          </h2>
          <p className="text-gray-600 mb-6">
            You don't have permission to edit this task.
          </p>
          <Link href="/tasks">
            <Button>Back to Tasks</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Link
          href="/tasks"
          className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
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
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back to Tasks
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Edit Task</h1>
        <p className="text-gray-600 mt-2">
          Update the details for "{task?.title}"
        </p>
      </div>

      {/* General error message */}
      {errors.general && (
        <div
          className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4"
          role="alert"
        >
          <div className="flex items-start gap-3">
            <svg
              className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0"
              fill="currentColor"
              viewBox="0 0 20 20"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <div className="flex-1">
              <p className="text-sm font-medium text-red-800">
                {errors.general}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Form */}
      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-6"
      >
        {/* Title field */}
        <div>
          <label
            htmlFor="title"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Title <span className="text-red-600">*</span>
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title || ""}
            onChange={handleChange}
            onBlur={handleBlur}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              touched.title && errors.title
                ? "border-red-500"
                : "border-gray-300"
            }`}
            placeholder="Enter task title"
            aria-invalid={touched.title && errors.title ? "true" : "false"}
            aria-describedby={
              touched.title && errors.title ? "title-error" : "title-help"
            }
            maxLength={201}
          />
          <div className="mt-1 flex items-center justify-between">
            {touched.title && errors.title ? (
              <p id="title-error" className="text-sm text-red-600" role="alert">
                {errors.title}
              </p>
            ) : (
              <p id="title-help" className="text-sm text-gray-500">
                Required field
              </p>
            )}
            <span
              className={`text-sm ${
                (formData.title?.length || 0) > 200
                  ? "text-red-600"
                  : "text-gray-500"
              }`}
            >
              {formData.title?.length || 0}/200
            </span>
          </div>
        </div>

        {/* Description field */}
        <div>
          <label
            htmlFor="description"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Description
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description || ""}
            onChange={handleChange}
            onBlur={handleBlur}
            rows={4}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              touched.description && errors.description
                ? "border-red-500"
                : "border-gray-300"
            }`}
            placeholder="Enter task description (optional)"
            aria-invalid={
              touched.description && errors.description ? "true" : "false"
            }
            aria-describedby={
              touched.description && errors.description
                ? "description-error"
                : "description-help"
            }
            maxLength={2001}
          />
          <div className="mt-1 flex items-center justify-between">
            {touched.description && errors.description ? (
              <p
                id="description-error"
                className="text-sm text-red-600"
                role="alert"
              >
                {errors.description}
              </p>
            ) : (
              <p id="description-help" className="text-sm text-gray-500">
                Optional field
              </p>
            )}
            <span
              className={`text-sm ${
                (formData.description?.length || 0) > 2000
                  ? "text-red-600"
                  : "text-gray-500"
              }`}
            >
              {formData.description?.length || 0}/2000
            </span>
          </div>
        </div>

        {/* Priority field */}
        <div>
          <label
            htmlFor="priority"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Priority
          </label>
          <select
            id="priority"
            name="priority"
            value={formData.priority}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <p className="mt-1 text-sm text-gray-500">
            Select the priority level for this task
          </p>
        </div>

        {/* Due date field */}
        <div>
          <label
            htmlFor="due_date"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Due Date
          </label>
          <input
            type="date"
            id="due_date"
            name="due_date"
            value={formData.due_date || ""}
            onChange={handleChange}
            onBlur={handleBlur}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              touched.due_date && errors.due_date
                ? "border-red-500"
                : "border-gray-300"
            }`}
            aria-invalid={
              touched.due_date && errors.due_date ? "true" : "false"
            }
            aria-describedby={
              touched.due_date && errors.due_date
                ? "due_date-error"
                : "due_date-help"
            }
          />
          {touched.due_date && errors.due_date ? (
            <p
              id="due_date-error"
              className="mt-1 text-sm text-red-600"
              role="alert"
            >
              {errors.due_date}
            </p>
          ) : (
            <p id="due_date-help" className="mt-1 text-sm text-gray-500">
              Optional: Set a deadline for this task
            </p>
          )}
        </div>

        {/* Tags field (T026) */}
        <div>
          <label
            htmlFor="tags"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Tags
          </label>
          <TagSelector
            ref={tagSelectorRef}
            selectedTags={formData.tags || []}
            onChange={(tags) => setFormData((prev) => ({ ...prev, tags }))}
            placeholder="Add tags (e.g., work, urgent, personal)"
          />
        </div>

        {/* Form actions */}
        <div className="flex gap-4 pt-4">
          <Button
            type="submit"
            isLoading={isSubmitting}
            disabled={!isFormValid || isSubmitting}
            fullWidth={false}
            className="flex-1"
          >
            {isSubmitting ? "Saving..." : "Save Changes"}
          </Button>
          <Link href="/tasks" className="flex-1">
            <Button
              type="button"
              variant="secondary"
              disabled={isSubmitting}
              fullWidth
            >
              Cancel
            </Button>
          </Link>
        </div>
      </form>
    </div>
  );
}
