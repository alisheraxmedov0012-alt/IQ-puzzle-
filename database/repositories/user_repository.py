from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.user import User, UserStatistics
from database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_with_statistics(self, user_id: int) -> Optional[User]:
        """Foydalanuvchini statistikasi bilan birga yuklash (Eager Loading)."""
        query = select(User).where(User.id == user_id).options(selectinload(User.statistics))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_user_with_stats(self, user_obj: User) -> User:
        """Yangi foydalanuvchi va uning bo'sh statistikasini tranzaksiyada yaratish."""
        self.session.add(user_obj)
        await self.session.flush()
        
        stats = UserStatistics(user_id=user_obj.id)
        self.session.add(stats)
        await self.session.flush()
        return user_obj
      
