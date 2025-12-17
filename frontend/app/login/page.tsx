/**
 * Login Page
 *
 * Features (T035-T037):
 * - Email and password input form
 * - Form validation (email format, password required)
 * - Error handling (invalid credentials, network errors)
 * - Submit button with loading state
 * - Link to signup page
 * - Auto-redirect to /tasks if already authenticated
 * - Redirect to /tasks on success
 * - Display session expiration message (T040)
 */

"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { signIn, useSession } from "@/lib/auth-client";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { SessionExpiredAlert } from "@/components/alerts/SessionExpiredAlert";

interface FormErrors {
  email?: string;
  password?: string;
}

export default function LoginPage() {
  const router = useRouter();
  const { data: session, isPending } = useSession();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<FormErrors>({});
  const [generalError, setGeneralError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // T037: Auto-redirect if already authenticated
  useEffect(() => {
    if (!isPending && session) {
      router.push("/tasks");
    }
  }, [session, isPending, router]);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Email validation
    if (!email) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = "Please enter a valid email address";
    }

    // Password validation
    if (!password) {
      newErrors.password = "Password is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Clear previous errors
    setGeneralError("");
    setErrors({});

    // Validate form
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const result = await signIn(email, password);

      if (result.error) {
        // Handle specific error cases
        if (result.error.message?.includes("credentials") ||
            result.error.message?.includes("password") ||
            result.error.message?.includes("not found")) {
          setGeneralError("Invalid email or password. Please try again.");
        } else {
          setGeneralError(result.error.message || "Failed to sign in. Please try again.");
        }
      } else {
        // Success - redirect to tasks
        router.push("/tasks");
      }
    } catch (error) {
      // Network or unexpected errors
      console.error("Sign in error:", error);
      setGeneralError("Network error. Please check your connection and try again.");
    } finally {
      setIsLoading(false);
    }
  };

  // Show loading state while checking session
  if (isPending) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render form if already authenticated (will redirect)
  if (session) {
    return null;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      {/* T040: Session expiration detection with Suspense boundary */}
      <Suspense fallback={null}>
        <SessionExpiredAlert onExpired={setGeneralError} />
      </Suspense>

      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Manage your tasks efficiently
          </p>
        </div>

        {/* Form */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {/* General error message */}
          {generalError && (
            <ErrorMessage
              message={generalError}
              onDismiss={() => setGeneralError("")}
            />
          )}

          <div className="space-y-4">
            {/* Email input */}
            <Input
              id="email"
              label="Email address"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              error={errors.email}
              disabled={isLoading}
            />

            {/* Password input */}
            <Input
              id="password"
              label="Password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              error={errors.password}
              disabled={isLoading}
            />
          </div>

          {/* Submit button */}
          <Button
            type="submit"
            fullWidth
            isLoading={isLoading}
          >
            Sign in
          </Button>

          {/* Link to signup */}
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{" "}
              <Link
                href="/signup"
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                Sign up
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
