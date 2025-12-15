"use client";

/**
 * Navbar component with user session and logout (T038)
 *
 * Features:
 * - Display user email when authenticated
 * - Logout button that:
 *   - Calls Better-Auth logout
 *   - Clears session
 *   - Redirects to /login
 * - Responsive navigation bar
 * - Mobile-first design
 * - Only displays when user is authenticated
 */

import React from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { signOut, useSession } from "@/lib/auth-client";
import { Button } from "@/components/ui/Button";

export const Navbar: React.FC = () => {
  const router = useRouter();
  const { data: session, isPending } = useSession();
  const [isLoggingOut, setIsLoggingOut] = React.useState(false);

  // Handle logout
  const handleLogout = async () => {
    setIsLoggingOut(true);

    try {
      await signOut();
      // Redirect to login page after successful logout
      router.push("/login");
    } catch (error) {
      console.error("Logout error:", error);
      // Still redirect even if there's an error
      router.push("/login");
    } finally {
      setIsLoggingOut(false);
    }
  };

  // Don't render navbar if not authenticated or still loading
  if (isPending || !session) {
    return null;
  }

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and title */}
          <div className="flex items-center">
            <Link
              href="/tasks"
              className="text-xl font-bold text-gray-900 hover:text-blue-600 transition-colors"
            >
              Hackathon Todo
            </Link>
          </div>

          {/* User info and logout */}
          <div className="flex items-center space-x-4">
            {/* User email */}
            {session.user?.email && (
              <span className="text-sm text-gray-700 hidden sm:inline">
                {session.user.email}
              </span>
            )}

            {/* Logout button */}
            <Button
              variant="secondary"
              onClick={handleLogout}
              isLoading={isLoggingOut}
              disabled={isLoggingOut}
              className="text-sm"
            >
              {isLoggingOut ? "Logging out..." : "Logout"}
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
};
