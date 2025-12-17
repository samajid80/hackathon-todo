"use client";

import { useEffect, useRef } from "react";
import { useSearchParams, useRouter } from "next/navigation";

interface SessionExpiredAlertProps {
  onExpired: (message: string) => void;
}

/**
 * Detects session expiration from URL parameters and displays error message
 *
 * This component checks for ?expired=true in the URL and calls onExpired callback
 * when detected. It cleans up the URL parameter after processing.
 *
 * @param onExpired - Callback to display error message
 */
export function SessionExpiredAlert({ onExpired }: SessionExpiredAlertProps) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const processedRef = useRef(false);

  useEffect(() => {
    const isExpired = searchParams.get("expired") === "true";

    if (isExpired && !processedRef.current) {
      processedRef.current = true;
      onExpired("Your session has expired. Please sign in again.");

      // Clean up URL parameter
      router.replace("/login");
    }
  }, [searchParams, router, onExpired]);

  // This is a side-effect only component
  return null;
}
