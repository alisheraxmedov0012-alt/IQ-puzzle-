import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from core.config import settings
from core.logger import logger
from core.exceptions import PuzzleForgeException
from telegram.handlers.commands import command_router
from telegram.handlers.puzzle_handlers import game_router
from telegram.middlewares.db_middleware import DbSessionMiddleware
from telegram.middlewares.rate_limit import ThrottlingMiddleware

# 1. Telegram Bot va Dispatcher ob'ektlarini yaratamiz
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

# Middleware va routerlarni ulash
dp.update.middleware(DbSessionMiddleware())
dp.include_router(command_router)
dp.include_router(game_router)

# 2. To'g'ri Lifespan boshqaruvi (Webhookni xatosiz ulash joyi)
@asynccontextmanager
async def app_lifespan(fastapi_app: FastAPI):
    # Bu yer server ishga tushganda (startup) bajariladi
    from core.redis_client import redis_client
    dp.update.middleware(ThrottlingMiddleware(redis=redis_client))
    
    # Railway bergan aniq domen manzili
    webhook_url = "https://iq-puzzle-production.up.railway.app/webhook/bot"
    
    await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
    logger.info(f"🔥 Telegram Webhook muvaffaqiyatli o'rnatildi: {webhook_url}")
    
    yield
    # Bu yer server to'xtaganda (shutdown) bajariladi
    await bot.delete_webhook()

# 3. FastAPI ilovasini yangi lifespan bilan yaratamiz
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=app_lifespan,
    docs_url="/docs" if settings.DEBUG else None
)

@app.post("/webhook/bot")
async def telegram_webhook(request: Request) -> JSONResponse:
    """Telegramdan keladigan har bir xabarni qabul qiluvchi yagona endpoint."""
    try:
        update_json = await request.json()
        update = Update.model_validate(update_json, context={"bot": bot})
        
        # Aiogram xabarni orqa fonda tezkor qayta ishlaydi
        asyncio.create_task(dp.feed_update(bot, update))
        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "queued"})
    except Exception as e:
        logger.error(f"Webhookda xatolik: {str(e)}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Invalid payload"})

@app.exception_handler(PuzzleForgeException)
async def custom_exception_handler(request: Request, exc: PuzzleForgeException) -> JSONResponse:
    logger.warning(f"Kutilgan istisno: Kod: {exc.code} | Xabar: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "error_code": exc.code, "message": exc.message}
        )
    
