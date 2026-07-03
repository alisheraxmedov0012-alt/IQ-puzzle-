import sys
from pathlib import Path
from loguru import logger

# Loglarni saqlash uchun log papkasini yaratamiz
LOG_DIR = Path("storage/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

def setup_logging() -> None:
    """Tizim miqyosida ishlovchi logging konfiguratsiyasi."""
    # Eski standart handlerlarni tozalaymiz
    logger.remove()

    # Konsolga chiqadigan log format (Raqamli va chiroyli)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG",
        enqueue=True
    )

    # Faylga yoziladigan JSON format (Production analitika uchun)
    logger.add(
        LOG_DIR / "app_error.log",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        level="ERROR",
        serialize=True,
        enqueue=True
    )
    
    logger.add(
        LOG_DIR / "app_info.log",
        rotation="50 MB",
        retention="10 days",
        level="INFO",
        enqueue=True
    )
  
