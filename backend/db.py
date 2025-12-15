"""Database connection and session management.

This module provides SQLModel engine setup and session management for
PostgreSQL (Neon) database access with performance logging (T149).
"""

import logging
import os
import time
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Configure database logger (T149)
logger = logging.getLogger("database")


def get_database_url() -> str:
    """Get database URL from environment, with validation.

    Returns:
        str: Database connection URL

    Raises:
        ValueError: If DATABASE_URL is not set (in non-test environment)
    """
    url = os.getenv("DATABASE_URL", "")
    if not url:
        raise ValueError(
            "DATABASE_URL environment variable is not set. "
            "Please configure it in .env file or environment."
        )
    return url


def create_db_engine():
    """Create SQLModel database engine with performance logging (T149).

    Returns:
        Engine: SQLModel engine instance

    Note:
        Query logging is enabled in development mode via echo=True and
        custom event listeners for performance tracking.
    """
    database_url = get_database_url()
    is_development = os.getenv("ENVIRONMENT", "development") == "development"

    # Use StaticPool for SQLite (testing), connection pooling for PostgreSQL
    if database_url.startswith("sqlite"):
        engine = create_engine(
            database_url,
            echo=is_development,  # Log SQL queries in development
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(
            database_url,
            echo=is_development,  # Log SQL queries in development
            pool_pre_ping=True,  # Verify connections before using them
            pool_size=5,  # Connection pool size
            max_overflow=10,  # Maximum overflow connections
        )

    # T149: Add performance logging event listeners for development
    if is_development:
        from sqlalchemy import event

        @event.listens_for(engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Record query start time for performance measurement."""
            context._query_start_time = time.time()

        @event.listens_for(engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Log query execution time and index usage."""
            total_time = time.time() - context._query_start_time

            # Extract query type and table info
            query_type = statement.strip().split()[0].upper()

            # Sanitize parameters (remove sensitive data like passwords)
            safe_params = parameters
            if isinstance(parameters, dict):
                safe_params = {k: '***' if 'password' in k.lower() else v
                              for k, v in parameters.items()}

            # Log basic query info
            logger.debug(
                f"[DB] {query_type} query executed in {total_time*1000:.2f}ms | "
                f"Params: {safe_params}"
            )

            # For SELECT queries on tasks table, check if indexes are used
            if query_type == "SELECT" and "tasks" in statement.lower():
                # Check for common indexed columns
                uses_user_id_index = "user_id" in statement.lower()
                uses_status = "status" in statement.lower() and "WHERE" in statement.upper()
                uses_due_date = (
                    "due_date" in statement.lower() and "ORDER BY" in statement.upper()
                )

                index_info = []
                if uses_user_id_index:
                    index_info.append("user_id index")
                if uses_status:
                    index_info.append("status index")
                if uses_due_date:
                    index_info.append("due_date index")

                if index_info:
                    logger.debug(f"[DB] Index usage: {', '.join(index_info)}")
                else:
                    logger.warning("[DB] Potential full table scan detected")

    return engine


# Create the global engine instance
# This will be initialized when the module is imported
# For tests, DATABASE_URL should be set before importing this module
try:
    engine = create_db_engine()
except ValueError:
    # In test environment, engine will be created explicitly
    engine = None  # type: ignore


def get_session() -> Generator[Session]:
    """Dependency function to get database session.

    Yields a SQLModel Session for database operations.
    Automatically closes the session after use.

    Usage:
        @app.get("/tasks")
        def get_tasks(session: Session = Depends(get_session)):
            ...

    Yields:
        Session: SQLModel database session
    """
    if engine is None:
        msg = "Database engine not initialized. Set DATABASE_URL environment variable."
        raise ValueError(msg)
    with Session(engine) as session:
        yield session


def create_db_and_tables() -> None:
    """Create all database tables.

    This function should be called on application startup to ensure
    all tables exist. In production, use Alembic migrations instead.

    Note:
        Better-Auth manages the users table automatically.
        This function only creates the tasks table.
    """
    if engine is None:
        msg = "Database engine not initialized. Set DATABASE_URL environment variable."
        raise ValueError(msg)

    from .models.task import Task  # noqa: F401 - Import required for table creation

    SQLModel.metadata.create_all(engine)
