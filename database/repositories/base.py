from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from database.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Barcha repository'lar uchun bazaviy CRUD operatsiyalari sinfi."""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: Any) -> Optional[ModelType]:
        """ID bo'yicha bitta yozuvni olish."""
        return await self.session.get(self.model, id)

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Ko'plab yozuvlarni pagination bilan olish."""
        query = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, obj_in: ModelType) -> ModelType:
        """Yangi yozuv yaratish."""
        self.session.add(obj_in)
        await self.session.flush()  # ID generation uchun flush qilamiz
        return obj_in

    async def update(self, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """Mavjud yozuvni yangilash."""
        for field in obj_in:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_in[field])
        self.session.add(db_obj)
        await self.session.flush()
        return db_obj

    async def delete(self, id: Any) -> Optional[ModelType]:
        """ID bo'yicha yozuvni o'chirish."""
        obj = await self.session.get(self.model, id)
        if obj:
            await self.session.delete(obj)
            await self.session.flush()
        return obj
      
