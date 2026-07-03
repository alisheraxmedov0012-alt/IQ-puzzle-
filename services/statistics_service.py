from typing import Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.user import UserStatistics
from database.models.puzzle import PuzzleSession, SessionStatus
from database.repositories.user_repository import UserRepository
from core.logger import logger


class StatisticsService:
    """Foydalanuvchi ko'rsatkichlari va platforma reytinglarini hisoblovchi servis."""

    def __init__(self, user_repo: UserRepository, session: AsyncSession):
        self.user_repo = user_repo
        self.session = session

    async def update_user_metrics(self, user_id: int, last_session: PuzzleSession) -> UserStatistics:
        """Oxirgi o'yin natijasiga qarab foydalanuvchi statistikasini yangilaydi."""
        user = await self.user_repo.get_with_statistics(user_id)
        if not user or not user.statistics:
            raise ValueError(f"Foydalanuvchi statistikasi topilmadi: {user_id}")

        stats = user.statistics

        if last_session.status == SessionStatus.SOLVED:
            stats.puzzles_solved += 1
            # To'g'ri javob uchun ball (Tezkorlikka qarab bonus beriladi)
            base_score = 100
            time_bonus = max(0, 60 - (last_session.solve_time or 60))
            stats.total_score += (base_score + time_bonus)
            
            # IQ darajasini oshirish (+3 ball)
            stats.iq_rating += 3
        
        elif last_session.status == SessionStatus.FAILED or last_session.status == SessionStatus.TIMEOUT:
            stats.puzzles_failed += 1
            # Xato uchun IQ darajasi biroz tushadi (-1 ball, lekin 50 dan pastga tushmaydi)
            stats.iq_rating = max(50, stats.iq_rating - 1)

        # O'rtacha yechish vaqtini qayta hisoblash (Rolling Average)
        total_games = stats.puzzles_solved + stats.puzzles_failed
        if total_games > 0:
            current_solve_time = last_session.solve_time or 0
            stats.average_solve_time = (
                (stats.average_solve_time * (total_games - 1)) + current_solve_time
            ) / total_games

        # Bazaga saqlash
        self.session.add(stats)
        await self.session.flush()
        
        logger.info(f"Foydalanuvchi {user_id} statistikasi yangilandi. Yangi IQ: {stats.iq_rating}")
        return stats

    async def get_global_leaderboard(self, limit: int = 10) -> list:
        """Eng yuqori ball to'plagan foydalanuvchilar ro'yxatini qaytaradi."""
        query = (
            select(UserStatistics)
            .order_by(UserStatistics.total_score.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
      
