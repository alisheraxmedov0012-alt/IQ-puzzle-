import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from core.config import settings
from core.logger import logger
from core.exceptions import PuzzleForgeException
from app.lifespan import lifespan
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

# 2. Loyihangizning o'z asl lifespan funksiyasini kengaytiramiz
@asynccontextmanager
async def app_lifespan(fastapi_app: FastAPI):
    # Loyihangizning o'z maxsus lifespan kodini ishga tushiramiz (Baza va Redis ulanadi)
    async with lifespan(fastapi_app):
        # Throttling middleware'ga loyihangiz ulagan tayyor redis obyektini uzatamiz
        dp.update.middleware(ThrottlingMiddleware(redis=fastapi_app.state.redis))
        
        # Railway bergan aniq domen manzili
        webhook_url = "https://iq-puzzle-production.up.railway.app/webhook/bot"
        
        await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
        logger.info(f"🔥 Telegram Webhook muvaffaqiyatli o'rnatildi: {webhook_url}")
        
        yield
        
        # Server o'chganda webhookni tozalaymiz
        await bot.delete_webhook()

# 3. FastAPI ilovasini yangilangan lifespan bilan yaratamiz
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
    
