from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
from src.core.config import settings

engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=True if settings.ENV == "development" else False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Inyector de sesión básica de base de datos."""
    async with AsyncSessionLocal() as session:
        yield session

async def set_tenant_session(session: AsyncSession, tenant_id: str):
    """Setea la variable de sesión en PostgreSQL para aplicar la política RLS Multi-Tenant."""
    await session.execute(
        f"SET LOCAL app.current_tenant_id = '{tenant_id}';"
    )