"""
BHOOMI-X Database Setup
SQLAlchemy async engine with PostGIS support via GeoAlchemy2.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event
from config import settings


def _get_async_db_url(url: str) -> str:
    """Ensure database URL uses the asyncpg driver."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


# Async engine for FastAPI
DATABASE_URL = _get_async_db_url(settings.DATABASE_URL)

# Disable statement cache unconditionally for asyncpg so it NEVER fails on PgBouncer / Supabase / Cloud poolers
connect_args = {
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0,
}

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    connect_args=connect_args,
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency: yields a database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables. Called on app startup."""
    import models  # noqa: F401
    import logging
    log = logging.getLogger("bhoomix")

    try:
        async with engine.begin() as conn:
            # Enable PostGIS extension
            await conn.execute(
                __import__("sqlalchemy").text("CREATE EXTENSION IF NOT EXISTS postgis")
            )
            # Create all tables if they don't exist
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        log.warning(f"Database initialization encountered warning/notice (safe to continue): {e}")


async def close_db():
    """Dispose engine. Called on app shutdown."""
    await engine.dispose()
