from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from core.config import settings
from core.logger import logger

# Asinxron Engine yaratamiz
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10
)

# Async Session Factory
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependencies yoki boshqa joylarda Context Manager uchun session yaratuvchi."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Database tranzaksiya jarayonida xatolik: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()
          
