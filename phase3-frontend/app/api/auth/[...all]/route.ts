/**
 * Better-Auth API Route Handler for Phase 3 Frontend.
 *
 * This catch-all route handles all Better-Auth requests:
 * - POST /api/auth/sign-up - Create new user account
 * - POST /api/auth/sign-in - Authenticate user
 * - POST /api/auth/sign-out - End user session
 * - GET  /api/auth/session - Get current session
 * - GET  /api/auth/jwks - Get JSON Web Key Set (public keys)
 *
 * Better-Auth automatically handles:
 * - User creation and validation
 * - Password hashing (bcrypt)
 * - JWT token generation (EdDSA)
 * - Session management
 * - Database operations (users table)
 * - JWKS endpoint for token verification
 */

import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";
import { NextRequest } from "next/server";

const handlers = toNextJsHandler(auth);

export async function GET(req: NextRequest) {
  try {
    console.log("[Phase3 Auth API GET] Path:", req.nextUrl.pathname);
    return await handlers.GET(req);
  } catch (error) {
    console.error("[Phase3 Auth API GET Error]:", error);
    throw error;
  }
}

export async function POST(req: NextRequest) {
  try {
    console.log("[Phase3 Auth API POST] Path:", req.nextUrl.pathname);
    console.log("[Phase3 Auth API POST] Starting at:", new Date().toISOString());

    const result = await handlers.POST(req);

    console.log("[Phase3 Auth API POST] Completed at:", new Date().toISOString());
    console.log("[Phase3 Auth API POST] Response status:", result.status);

    // Log response headers for JWT debugging
    const clonedResponse = result.clone();
    const body = await clonedResponse.text();
    console.log("[Phase3 Auth API POST] Response body:", body.substring(0, 500));

    return result;
  } catch (error) {
    console.error("[Phase3 Auth API POST Error]:", error);
    console.error("[Phase3 Auth API POST Error Type]:", error?.constructor?.name);
    console.error("[Phase3 Auth API POST Error Code]:", (error as any)?.code);
    console.error("[Phase3 Auth API POST Error Message]:", (error as any)?.message);
    console.error("[Phase3 Auth API POST Error Stack]:", error instanceof Error ? error.stack : 'No stack');

    // Log all error properties
    if (error && typeof error === 'object') {
      console.error("[Phase3 Auth API POST Error Details]:", JSON.stringify(error, Object.getOwnPropertyNames(error), 2));
    }

    throw error;
  }
}
