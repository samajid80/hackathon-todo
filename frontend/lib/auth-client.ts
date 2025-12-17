/**
 * Better-Auth client configuration for frontend
 *
 * This provides client-side authentication methods:
 * - Sign up with email/password
 * - Sign in with email/password
 * - Sign out
 * - Get current session
 */

import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_AUTH_URL || "http://localhost:3000/api/auth",
  plugins: [jwtClient()],
});

/**
 * Sign up a new user
 */
export async function signUp(email: string, password: string, name: string) {
  return authClient.signUp.email({
    email,
    password,
    name,
  });
}

/**
 * Sign in an existing user
 */
export async function signIn(email: string, password: string) {
  return authClient.signIn.email({
    email,
    password,
  });
}

/**
 * Sign out current user
 */
export async function signOut() {
  return authClient.signOut();
}

/**
 * Get current session
 */
export async function getSession() {
  return authClient.getSession();
}

/**
 * Use session hook for React components
 */
export const useSession = authClient.useSession;
