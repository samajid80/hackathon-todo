/**
 * Next.js Middleware for route protection (T039)
 *
 * Features:
 * - Check if user is authenticated via Better-Auth session
 * - Public routes: /login, /signup, / (homepage)
 * - Protected routes: /tasks and all subroutes
 * - Redirect unauthenticated users to /login
 * - Preserve redirect intent (return to original path after login)
 * - Session expiration handling
 */

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Define public routes that don't require authentication
const publicRoutes = ["/login", "/signup", "/"];

// Define routes that should redirect to /tasks if authenticated
const authRoutes = ["/login", "/signup"];

/**
 * Middleware function to protect routes
 */
export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check if the current route is public
  const isPublicRoute = publicRoutes.includes(pathname);

  // Check if the current route is an auth route (login/signup)
  const isAuthRoute = authRoutes.includes(pathname);

  // Get the session token from cookies
  // Better-Auth stores the session in a cookie named: hackathon-todo.session-token
  const sessionToken = request.cookies.get("hackathon-todo.session-token");
  const isAuthenticated = !!sessionToken;

  // If user is authenticated and trying to access auth routes (login/signup)
  // redirect them to /tasks
  if (isAuthenticated && isAuthRoute) {
    return NextResponse.redirect(new URL("/tasks", request.url));
  }

  // If user is not authenticated and trying to access protected routes
  // redirect them to /login
  if (!isAuthenticated && !isPublicRoute) {
    // Build the login URL with redirect parameter
    const loginUrl = new URL("/login", request.url);

    // Preserve the original path for redirect after login
    if (pathname !== "/") {
      loginUrl.searchParams.set("redirect", pathname);
    }

    // Add session expiration flag if applicable
    // This can be enhanced to check if the session actually expired
    // vs. user never being logged in
    const response = NextResponse.redirect(loginUrl);

    return response;
  }

  // Allow the request to proceed
  return NextResponse.next();
}

/**
 * Configure which routes the middleware should run on
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (images, etc.)
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
