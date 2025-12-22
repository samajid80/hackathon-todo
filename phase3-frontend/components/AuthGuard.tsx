/**
 * AuthGuard component for protecting routes.
 *
 * Redirects unauthenticated users to login page.
 * Shows loading spinner while checking authentication status.
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { authClient } from "@/lib/auth-client";
import LoadingSpinner from "./LoadingSpinner";

interface AuthGuardProps {
  children: React.ReactNode;
}

export default function AuthGuard({ children }: AuthGuardProps) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const router = useRouter();

  useEffect(() => {
    async function checkAuth() {
      try {
        const session = await authClient.getSession();

        if (!session) {
          // No session, redirect to login
          router.push("/login");
          setIsAuthenticated(false);
        } else {
          // Authenticated
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error("Auth check failed:", error);
        router.push("/login");
        setIsAuthenticated(false);
      }
    }

    checkAuth();
  }, [router]);

  // Show loading spinner while checking authentication
  if (isAuthenticated === null) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  // Don't render children if not authenticated (during redirect)
  if (!isAuthenticated) {
    return null;
  }

  // Render protected content
  return <>{children}</>;
}
