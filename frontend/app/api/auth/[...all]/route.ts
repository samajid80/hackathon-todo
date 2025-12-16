/**
 * Better-Auth API Route Handler
 *
 * This catch-all route handles all Better-Auth requests:
 * - POST /api/auth/sign-up - Create new user account
 * - POST /api/auth/sign-in - Authenticate user
 * - POST /api/auth/sign-out - End user session
 * - GET  /api/auth/session - Get current session
 * - POST /api/auth/jwt/create - Create JWT token (JWT plugin)
 *
 * Better-Auth automatically handles:
 * - User creation and validation
 * - Password hashing (bcrypt)
 * - JWT token generation
 * - Session management
 * - Database operations (users table)
 */

import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

// Export all HTTP method handlers directly from Better-Auth
// This ensures JWT plugin endpoints (/api/auth/jwt/create) are properly exposed
export const { GET, POST } = toNextJsHandler(auth);
