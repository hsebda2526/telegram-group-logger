# app_common/db.py
# Создание асинхронного подключения к Postgres и фабрики сессий


import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession




def _db_url() -> str:
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "telegram")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"


engine = create_async_engine(_db_url(), echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncSession:
    """Создать новую асинхронную сессию БД."""
    async with AsyncSessionLocal() as session:
        yield session