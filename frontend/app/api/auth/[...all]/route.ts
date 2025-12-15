/**
 * Better-Auth API Route Handler
 *
 * This catch-all route handles all Better-Auth requests:
 * - POST /api/auth/sign-up - Create new user account
 * - POST /api/auth/sign-in - Authenticate user
 * - POST /api/auth/sign-out - End user session
 * - GET  /api/auth/session - Get current session
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
import { NextRequest } from "next/server";

const handlers = toNextJsHandler(auth);

export async function GET(req: NextRequest) {
  try {
    return await handlers.GET(req);
  } catch (error) {
    console.error("[Auth API GET Error]:", error);
    throw error;
  }
}

export async function POST(req: NextRequest) {
  try {
    console.log("[Auth API POST] Path:", req.nextUrl.pathname);
    const result = await handlers.POST(req);
    console.log("[Auth API POST] Response status:", result.status);

    // Log response body for debugging
    const clonedResponse = result.clone();
    const body = await clonedResponse.text();
    console.log("[Auth API POST] Response body:", body.substring(0, 500));

    return result;
  } catch (error) {
    console.error("[Auth API POST Error]:", error);
    console.error("[Auth API POST Error Stack]:", error instanceof Error ? error.stack : 'No stack');
    throw error;
  }
}
