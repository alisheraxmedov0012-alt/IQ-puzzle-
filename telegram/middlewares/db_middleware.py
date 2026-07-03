from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from database.session import async_session_factory
from database.repositories.user_repository import UserRepository
from database.repositories.puzzle_repository import PuzzleRepository, PuzzleSessionRepository
from services.puzzle_service import PuzzleService
from engines.renderer.image_renderer import ImageRenderingEngine

# Yagona renderer instance (Keshdan unumli foydalanish uchun)
renderer_engine = ImageRenderingEngine()


class DbSessionMiddleware(BaseMiddleware):
    """Har bir so'rovga avtomatlashtirilgan DB context va Servislarni yuklovchi middleware."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with async_session_factory() as session:
            # Repository'larni yaratamiz
            user_repo = UserRepository(session)
            puzzle_repo = PuzzleRepository(session)
            session_repo = PuzzleSessionRepository(session)
            
            # Servisni orkestratsiya qilamiz
            puzzle_service = PuzzleService(
                user_repo=user_repo,
                puzzle_repo=puzzle_repo,
                session_repo=session_repo,
                renderer=renderer_engine
            )
            
            # Ma'lumotlarni handlerlarga dependency sifatida uzatamiz
            data["session"] = session
            data["user_repo"] = user_repo
            data["puzzle_service"] = puzzle_service
            
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise
              
