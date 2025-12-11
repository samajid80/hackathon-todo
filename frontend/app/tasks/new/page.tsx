/**
 * Task Creation Page (T061, T062, T063, T064, T065)
 *
 * Features:
 * - Form with fields: Title (required), Description (optional), Priority (dropdown), Due date (optional)
 * - Submit button: "Create Task"
 * - Cancel button: Back to /tasks
 * - Loading state during submission
 * - Success: redirect to /tasks
 * - Error handling with error messages
 * - Title required and not empty
 * - Title max 200 characters
 * - Description max 2000 characters
 * - Priority must be valid enum
 * - Due date must be valid date format
 * - Real-time validation errors
 * - Disable submit until form is valid
 * - Show character count for title/description
 */

"use client";

import React, { useState, FormEvent, ChangeEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { createTask } from "@/lib/api/tasks";
import { TaskCreate, Priority } from "@/types/task";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

interface FormErrors {
  title?: string;
  description?: string;
  due_date?: string;
}

export default function NewTaskPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<TaskCreate>({
    title: "",
    description: null,
    due_date: null,
    priority: "medium",
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  // Validate a single field
  const validateField = (
    name: keyof TaskCreate,
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
    const processedValue =
      value === "" || value === null ? null : value;

    setFormData((prev) => ({
      ...prev,
      [name]: processedValue,
    }));

    // Validate if field has been touched
    if (touched[name]) {
      const error = validateField(name as keyof TaskCreate, processedValue);
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

    const processedValue =
      value === "" || value === null ? null : value;
    const error = validateField(name as keyof TaskCreate, processedValue);
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
      await createTask(formData);
      // Redirect to tasks page with success message
      router.push("/tasks?created=true");
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to create task";
      setErrors({
        ...errors,
        title: errorMessage,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Check if form is valid for submit button
  const isFormValid =
    formData.title.trim().length > 0 &&
    formData.title.length <= 200 &&
    (!formData.description || formData.description.length <= 2000) &&
    Object.keys(errors).length === 0;

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
        <h1 className="text-3xl font-bold text-gray-900">Create New Task</h1>
        <p className="text-gray-600 mt-2">
          Fill in the details below to create a new task.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-6">
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
            value={formData.title}
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
                formData.title.length > 200
                  ? "text-red-600"
                  : "text-gray-500"
              }`}
            >
              {formData.title.length}/200
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

        {/* Form actions */}
        <div className="flex gap-4 pt-4">
          <Button
            type="submit"
            isLoading={isSubmitting}
            disabled={!isFormValid || isSubmitting}
            fullWidth={false}
            className="flex-1"
          >
            {isSubmitting ? "Creating..." : "Create Task"}
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
