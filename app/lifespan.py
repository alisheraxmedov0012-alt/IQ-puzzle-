from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from redis.asyncio import Redis
from core.config import settings
from core.logger import setup_logging, logger
from database.session import async_engine
from telegram.middlewares.db_middleware import renderer_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Loyiha startup va shutdown jarayonlarini xavfsiz boshqarish."""
    # ---- STARTUP ----
    setup_logging()
    logger.info("PuzzleForge backend tizimi ishga tushmoqda...")
    
    # Redis ulanishini tekshiramiz va FastAPI app xotirasiga bog'laymiz
    app.state.redis = Redis(
        host=settings.REDIS_HOST, 
        port=settings.REDIS_PORT, 
        db=settings.REDIS_DB,
        decode_responses=True
    )
    logger.info("Redis ulanishi muvaffaqiyatli o'rnatildi.")
    
    yield
    
    # ---- SHUTDOWN ----
    logger.info("Resurslar yopilmoqda...")
    await app.state.redis.close()
    await async_engine.dispose()
    logger.info("PuzzleForge tizimi muvaffaqiyatli to'xtatildi.")
  
