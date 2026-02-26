"""Alembic environment configuration for database migrations."""

import asyncio
import logging
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import settings and models
from src.core.config import settings
from src.database.base import Base
from src.database.models import *  # noqa: F401, F403

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger("alembic.env")

# Set the SQLAlchemy URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        logger.info("Running migrations in offline mode")
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Execute migrations with the given connection.

    Args:
        connection: SQLAlchemy connection to use for migrations
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        logger.info("Running migrations")
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode.

    Creates an async engine and runs migrations in an async context.
    """
    # Get database URL and convert to async driver if needed
    db_url = config.get_main_option("sqlalchemy.url")

    if db_url.startswith("sqlite://"):
        db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = db_url

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async support.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    try:
        asyncio.run(run_async_migrations())
    except Exception as e:
        logger.error("Error running migrations: %s", str(e), exc_info=True)
        raise


if context.is_offline_mode():
    logger.info("Running in offline mode")
    run_migrations_offline()
else:
    logger.info("Running in online mode")
    run_migrations_online()
