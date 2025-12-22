"""
Main FastAPI application for Phase 3 Backend (Chat Service).

Handles chat endpoint, conversation management, and OpenAI integration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.config import settings
from app.db import init_db, get_session
from app.routes import health, chat
from app.auth.rate_limiter import RateLimitMiddleware


# Background task to keep database warm
async def keep_database_warm():
    """
    Background task to prevent Neon database from going into cold start.

    Neon free tier auto-suspends after 5 minutes of inactivity.
    This task runs a simple query every 4 minutes to keep it active.
    """
    while True:
        try:
            await asyncio.sleep(240)  # Sleep 4 minutes

            # Simple query to keep connection alive
            async for session in get_session():
                from sqlmodel import text
                await session.execute(text("SELECT 1"))
                print("🔥 Database keepalive ping sent")
                break
        except Exception as e:
            print(f"⚠️  Database keepalive failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.

    Handles startup and shutdown events.
    """
    # Startup
    print("🚀 Starting Phase 3 Backend (Chat Service)...")

    # T098: Verify JWT secret is configured
    if len(settings.jwt_secret) < 32:
        raise ValueError(
            "JWT_SECRET must be at least 32 characters for security. "
            f"Current length: {len(settings.jwt_secret)}"
        )
    print(f"✅ JWT configuration validated (algorithm: {settings.jwt_algorithm})")

    # Verify OpenAI API key is configured
    if not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key-here":
        raise ValueError(
            "OPENAI_API_KEY must be configured in environment variables"
        )
    print("✅ OpenAI API key configured")

    # Verify MCP server URL is configured
    if not settings.mcp_server_url:
        raise ValueError(
            "MCP_SERVER_URL must be configured in environment variables"
        )
    print(f"✅ MCP server URL configured: {settings.mcp_server_url}")

    # Initialize database
    await init_db()
    print("✅ Database initialized")

    # Start background task to keep database warm
    keepalive_task = asyncio.create_task(keep_database_warm())
    print("✅ Database keepalive started (pings every 4 minutes)")

    yield

    # Shutdown
    print("👋 Shutting down Phase 3 Backend...")
    keepalive_task.cancel()
    try:
        await keepalive_task
    except asyncio.CancelledError:
        pass


# Create FastAPI app
app = FastAPI(
    title="Phase 3 Backend - AI Chat Service",
    description="Chat endpoint for natural language todo management",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware (T090)
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, tags=["Chat"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Phase 3 Backend - AI Chat Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }
