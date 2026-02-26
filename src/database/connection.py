"""Database connection and session management."""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.core.config import settings

logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """Get the database URL with async driver support.

    Returns:
        str: Database URL with async driver (e.g., postgresql+asyncpg)

    Raises:
        ValueError: If DATABASE_URL is not properly configured
    """
    db_url = settings.DATABASE_URL

    if not db_url:
        logger.error("DATABASE_URL not configured")
        raise ValueError("DATABASE_URL environment variable must be set")

    # Convert sqlite:// to sqlite+aiosqlite://
    if db_url.startswith("sqlite://"):
        async_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        logger.debug("Converted SQLite URL to async driver: %s", async_url)
        return async_url

    # Convert postgresql:// to postgresql+asyncpg://
    if db_url.startswith("postgresql://"):
        async_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        logger.debug("Converted PostgreSQL URL to async driver")
        return async_url

    # Check if already using async driver
    if "+asyncpg://" in db_url or "+aiosqlite://" in db_url:
        logger.debug("Database URL already uses async driver")
        return db_url

    logger.warning(
        "Unknown database URL format, returning as-is. "
        "Ensure it uses an async driver (asyncpg, aiosqlite, etc.)"
    )
    return db_url


# Create async engine with connection pooling
engine = create_async_engine(
    get_database_url(),
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    poolclass=NullPool if "sqlite" in get_database_url() else None,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection for database sessions.

    Yields:
        AsyncSession: Database session for async operations

    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            logger.debug("Database session created")
            yield session
            await session.commit()
            logger.debug("Database session committed successfully")
        except Exception as e:
            await session.rollback()
            logger.error(
                "Database session error, rolled back: %s",
                str(e),
                exc_info=True,
            )
            raise
        finally:
            await session.close()
            logger.debug("Database session closed")


async def check_database_connection() -> bool:
    """Check if database connection is healthy.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        logger.info("Database connection check successful")
        return True
    except Exception as e:
        logger.error(
            "Database connection check failed: %s",
            str(e),
            exc_info=True,
        )
        return False


async def close_database_connections() -> None:
    """Close all database connections gracefully.

    Should be called during application shutdown.
    """
    try:
        await engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(
            "Error closing database connections: %s",
            str(e),
            exc_info=True,
        )
