/**
 * useAuth Hook - Client-side authentication state management
 *
 * This hook wraps Better-Auth's useSession() to provide a simple,
 * type-safe interface for checking authentication status across the app.
 *
 * Usage:
 * ```tsx
 * const { user, isAuthenticated, isLoading } = useAuth();
 *
 * if (isLoading) return <LoadingSpinner />;
 * if (isAuthenticated) return <AuthenticatedView user={user} />;
 * return <UnauthenticatedView />;
 * ```
 */

'use client';

import { useSession } from '@/lib/auth-client';

/**
 * User object returned from Better-Auth session
 */
export interface AuthUser {
  id: string;
  email: string;
  name: string;
  emailVerified: boolean;
  image?: string | null;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Return type for useAuth hook
 */
export interface UseAuthReturn {
  /** Current authenticated user, or null if not authenticated */
  user: AuthUser | null;

  /** True if user is authenticated and session is valid */
  isAuthenticated: boolean;

  /** True while session status is being determined (prevents FOUC) */
  isLoading: boolean;
}

/**
 * Custom hook for accessing authentication state
 *
 * Provides a simple interface to check if user is authenticated,
 * get current user data, and handle loading states to prevent
 * flash of unauthenticated content (FOUC).
 *
 * @returns {UseAuthReturn} Authentication state object
 */
export function useAuth(): UseAuthReturn {
  const { data: session, isPending } = useSession();

  return {
    user: session?.user ?? null,
    isAuthenticated: !!session?.user,
    isLoading: isPending,
  };
}
