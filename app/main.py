import asyncio
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

# 1. FastAPI ilovasini yaratamiz
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None
)

# 2. Telegram Bot va Dispatcher obyektlarini yaratamiz
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

# Middleware'larni ro'yxatdan o'tkazamiz
dp.update.middleware(DbSessionMiddleware())

# Routerlarni ulash
dp.include_router(command_router)
dp.include_router(game_router)


@app.on_event("startup")
async def on_startup() -> None:
    """FastAPI ishga tushganda o'z navbatida bot middleware va webhooklarini sozlash."""
    # Throttling middleware uchun redis instance'ni uzatamiz
    dp.update.middleware(ThrottlingMiddleware(redis=app.state.redis))
    
    # Bot webhook manzilini o'rnatamiz (Production muhitida domen bo'lishi kerak)
    webhook_url = f"https://yourdomain.com/webhook/bot"
    await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
    logger.info(f"Telegram Webhook o'rnatildi: {webhook_url}")


@app.post("/webhook/bot")
async def telegram_webhook(request: Request) -> JSONResponse:
    """Telegramdan keladigan har bir xabarni (Update) qabul qiluvchi yagona endpoint."""
    try:
        update_json = await request.json()
        update = Update.model_validate(update_json, context={"bot": bot})
        
        # aiogram asinxron event loop ichida xabarni qayta ishlaydi
        asyncio.create_task(dp.feed_update(bot, update))
        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "queued"})
    except Exception as e:
        logger.error(f"Webhookda xatolik: {str(e)}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Invalid payload"})


@app.exception_handler(PuzzleForgeException)
async def custom_exception_handler(request: Request, exc: PuzzleForgeException) -> JSONResponse:
    """Tizimdagi barcha custom domen xatoliklarini tutib JSON ko'rinishida qaytaruvchi handler."""
    logger.warning(f"Kutilgan istisno: Kod: {exc.code} | Xabar: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "error_code": exc.code, "message": exc.message}
    )
  
