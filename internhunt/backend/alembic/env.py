"""
Alembic environment script for async SQLAlchemy.

Reads DATABASE_URL from environment variables (never hardcoded).
Supports both online (connected) and offline (SQL generation) modes.
"""

import asyncio
import os
from logging.config import fileConfig
from dotenv import load_dotenv

# Load environment variables from the project root .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Import all models so Alembic autogenerate can detect changes
from app.db.base import Base  # noqa: F401
import app.models  # noqa: F401 — registers all model classes

config = context.config

# Override sqlalchemy.url from environment variable
database_url = os.environ.get("DATABASE_URL", "")
if database_url:
    # Ensure async driver
    async_url = database_url.replace(
        "postgresql://", "postgresql+asyncpg://"
    ).replace("postgres://", "postgresql+asyncpg://")
    escaped_url = async_url.replace("%", "%%")
    config.set_main_option("sqlalchemy.url", escaped_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without a live database connection (generates SQL)."""
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
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create async engine and run migrations online."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
