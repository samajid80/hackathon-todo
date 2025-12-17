"use client";

import { useEffect, useRef } from "react";
import { useSearchParams, useRouter } from "next/navigation";

interface SuccessToastProps {
  paramName: "created" | "updated";
  message: string;
  onShow: (message: string) => void;
  onDetected?: () => void;
}

/**
 * Detects success URL parameters and displays toast notifications
 *
 * This component checks for specific URL parameters (e.g., ?created=true or ?updated=true)
 * and triggers success toast notifications. It also cleans up the URL parameter after processing.
 *
 * @param paramName - The URL parameter to check ("created" or "updated")
 * @param message - The success message to display
 * @param onShow - Callback to display the toast (e.g., toast.success)
 * @param onDetected - Optional callback to trigger after detection (e.g., refresh data)
 */
export function SuccessToast({
  paramName,
  message,
  onShow,
  onDetected,
}: SuccessToastProps) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const processedRef = useRef(false);

  useEffect(() => {
    const hasParam = searchParams.get(paramName) === "true";

    if (hasParam && !processedRef.current) {
      processedRef.current = true;
      onShow(message);

      // Clean up URL parameter
      router.replace("/tasks");

      // Trigger additional action (e.g., refresh task list)
      if (onDetected) {
        onDetected();
      }
    }
  }, [searchParams, router, paramName, message, onShow, onDetected]);

  // This is a side-effect only component
  return null;
}
