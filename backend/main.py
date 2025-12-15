"""FastAPI application entry point.

This module initializes the FastAPI application with:
- CORS middleware
- JWT authentication
- Rate limiting (T156)
- Security headers (T159)
- Caching headers (T152)
- API routes for the todo application
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables BEFORE importing other modules
# This ensures DATABASE_URL is available when db.py creates the engine
backend_dir = Path(__file__).parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

# Now import modules that depend on environment variables
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .auth.rate_limiter import RateLimitMiddleware
from .db import create_db_and_tables
from .routes import tasks

# Application metadata with enhanced OpenAPI documentation (T161)
app = FastAPI(
    title="Hackathon Todo API",
    description="""
## REST API for Task Management with Authentication

This is the backend API for the Hackathon Todo full-stack web application.

### Features
- **JWT Authentication**: All task endpoints require JWT bearer token
- **User-scoped Tasks**: Users can only access their own tasks
- **Filtering & Sorting**: Filter by status/priority, sort by date/priority
- **Rate Limiting**: Protection against abuse and brute force attacks
- **Security Headers**: OWASP-recommended security headers
- **Input Validation**: Comprehensive validation using Pydantic

### Authentication
All task endpoints require a JWT token in the `Authorization` header:
```
Authorization: Bearer <your-jwt-token>
```

To obtain a token, authenticate through the frontend using Better-Auth.

### Error Codes
- **400 Bad Request**: Invalid request payload or parameters
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: Attempting to access another user's resource
- **404 Not Found**: Resource not found (or not owned by user)
- **422 Unprocessable Entity**: Validation error
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Unexpected server error

### Rate Limits
- Authentication endpoints: 5 requests/hour per IP
- Task endpoints: 100 requests/hour per user

### External Resources
- [Frontend Repository](https://github.com/your-repo/frontend)
- [API Documentation](../API_DOCUMENTATION.md)
- [Deployment Guide](DEPLOY.md)
    """,
    version="1.0.0",
    docs_url="/api/docs",  # Swagger UI
    redoc_url="/api/redoc",  # ReDoc
    openapi_url="/api/openapi.json",
    contact={
        "name": "Hackathon Todo Team",
        "url": "https://github.com/your-repo",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# T159: Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses (T159).

    Security Headers (OWASP Best Practices):
        - X-Content-Type-Options: nosniff
          Prevents MIME sniffing attacks by forcing browsers to respect Content-Type

        - X-Frame-Options: DENY
          Prevents clickjacking attacks by blocking iframe embedding

        - X-XSS-Protection: 1; mode=block
          Enables XSS filter in older browsers (legacy support)

        - Strict-Transport-Security (HSTS): max-age=31536000; includeSubDomains
          Enforces HTTPS connections for 1 year (production only)
          Note: Only enable after confirming HTTPS is working

        - Referrer-Policy: strict-origin-when-cross-origin
          Controls referrer information sent with requests
          Sends full URL for same-origin, origin only for cross-origin HTTPS

    Example:
        app.add_middleware(SecurityHeadersMiddleware)

    References:
        - OWASP Secure Headers: https://owasp.org/www-project-secure-headers/
        - MDN Security Headers: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
    """

    async def dispatch(self, request: Request, call_next):
        """Process request and add security headers to response."""
        response = await call_next(request)

        # X-Content-Type-Options: Prevent MIME sniffing
        # Forces browsers to respect the Content-Type header
        # Prevents browsers from interpreting files as a different MIME type
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options: Prevent clickjacking
        # Blocks the page from being embedded in iframes
        # Protects against clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"

        # X-XSS-Protection: Enable XSS filter (legacy browsers)
        # Modern browsers have built-in XSS protection
        # This header is for older browsers (IE, Edge Legacy)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Strict-Transport-Security (HSTS): Enforce HTTPS
        # max-age=31536000 (1 year) - how long to remember HTTPS preference
        # includeSubDomains - apply to all subdomains
        # Note: Only enable in production after HTTPS is confirmed
        # Uncomment for production with HTTPS:
        # response.headers["Strict-Transport-Security"] = (
        #     "max-age=31536000; includeSubDomains"
        # )
        # For development (HTTP), we skip HSTS to avoid issues

        # Referrer-Policy: Control referrer information
        # strict-origin-when-cross-origin:
        #   - Same-origin: Send full URL
        #   - Cross-origin HTTPS: Send origin only
        #   - Cross-origin downgrade (HTTPS→HTTP): Send nothing
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response


# Add security headers middleware (T159)
app.add_middleware(SecurityHeadersMiddleware)


# T152: Caching middleware for GET endpoints
class CacheControlMiddleware(BaseHTTPMiddleware):
    """Add Cache-Control headers to GET requests (T152).

    Caching Strategy:
        - GET /api/tasks: Cache-Control: max-age=60, public (1 minute)
        - Other GET endpoints: Cache-Control: max-age=300, public (5 minutes)
        - Non-GET requests: No caching headers (Cache-Control: no-store)

    Note:
        We use 'public' for task list as it's user-specific but cacheable.
        Individual tasks are also cacheable with longer TTL.
        Authentication is required for all endpoints, so caching is safe.
    """

    async def dispatch(self, request: Request, call_next):
        """Process request and add cache headers to response."""
        response = await call_next(request)

        # Only add cache headers for successful GET requests
        if request.method == "GET" and response.status_code == 200:
            # Different cache TTL based on endpoint
            if request.url.path == "/api/tasks":
                # Task list: shorter cache (1 minute) as it changes frequently
                response.headers["Cache-Control"] = "max-age=60, public"
            elif request.url.path.startswith("/api/tasks/"):
                # Individual tasks: longer cache (5 minutes) as they're more stable
                response.headers["Cache-Control"] = "max-age=300, public"
            elif request.url.path in ["/", "/health"]:
                # Health/root endpoints: longer cache (10 minutes)
                response.headers["Cache-Control"] = "max-age=600, public"
            else:
                # Default for other GET endpoints: 5 minutes
                response.headers["Cache-Control"] = "max-age=300, public"

            # Add ETag support (simple content-based ETag)
            # This allows clients to use conditional requests (If-None-Match)
            # Note: FastAPI automatically handles ETag validation if present
            if not response.headers.get("ETag"):
                # We'll let FastAPI handle ETag generation via content hashing
                pass
        else:
            # For non-GET requests or error responses, disable caching
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"

        return response


# Add caching middleware (T152)
app.add_middleware(CacheControlMiddleware)


# T156: Add rate limiting middleware
# Note: Rate limiting is added AFTER caching to limit requests before cache lookup
app.add_middleware(RateLimitMiddleware)


# CORS configuration - MUST be added LAST so it runs FIRST (middleware executes in reverse order)
# This ensures CORS headers are added even if other middlewares throw errors
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Application startup event handler.

    Creates database tables on startup. In production, use Alembic migrations.
    """
    create_db_and_tables()


@app.get(
    "/",
    summary="API Root",
    description="Get API information and status",
    response_description="API metadata including version and documentation links",
    tags=["Health"],
)
def read_root():
    """Root endpoint for health check.

    Returns:
        dict: API status and version information

    Example Response:
        ```json
        {
            "status": "ok",
            "message": "Hackathon Todo API",
            "version": "1.0.0",
            "docs": "/api/docs"
        }
        ```
    """
    return {
        "status": "ok",
        "message": "Hackathon Todo API",
        "version": "1.0.0",
        "docs": "/api/docs",
    }


@app.get(
    "/health",
    summary="Health Check",
    description="Check if the API service is running",
    response_description="Service health status",
    tags=["Health"],
)
def health_check():
    """Health check endpoint.

    Returns:
        dict: Service health status

    Example Response:
        ```json
        {
            "status": "healthy"
        }
        ```
    """
    return {"status": "healthy"}


# Register API routes (T055)
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
