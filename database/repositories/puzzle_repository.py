from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.puzzle import Puzzle, PuzzleSession, SessionStatus, PuzzleType
from database.repositories.base import BaseRepository


class PuzzleRepository(BaseRepository[Puzzle]):
    def __init__(self, session: AsyncSession):
        super().__init__(Puzzle, session)

    async def get_by_hash(self, puzzle_hash: str) -> Optional[Puzzle]:
        """Xesh bo'yicha puzzleni qidirish (Duplicate oldini olish uchun)."""
        query = select(Puzzle).where(Puzzle.hash == puzzle_hash)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class PuzzleSessionRepository(BaseRepository[PuzzleSession]):
    def __init__(self, session: AsyncSession):
        super().__init__(PuzzleSession, session)

    async def get_active_session(self, user_id: int) -> Optional[PuzzleSession]:
        """Foydalanuvchining hozirda faol (yechilayotgan) puzzle seansini olish."""
        query = (
            select(PuzzleSession)
            .where(
                and_(
                    PuzzleSession.user_id == user_id,
                    PuzzleSession.status == SessionStatus.ACTIVE
                )
            )
            .options(selectinload(PuzzleSession.puzzle))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
      
