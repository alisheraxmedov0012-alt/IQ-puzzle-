import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from redis.asyncio import Redis
from core.config import settings


class ThrottlingMiddleware(BaseMiddleware):
    """Foydalanuvchilarni spamdan va botni yuklamadan himoya qiluvchi middleware."""

    def __init__(self, redis: Redis):
        self.redis = redis
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)

        user_id = event.from_user.id
        key = f"throttle:{user_id}"
        
        # Redis orqali so'rovlar sonini va vaqtini tekshiramiz
        current_time = time.time()
        request_count = await self.redis.incr(key)
        
        if request_count == 1:
            # Birinchi so'rov bo'lsa, uning muddati (TTL) ni belgilaymiz
            await self.redis.expire(key, settings.RATE_LIMIT_PERIOD)
        
        if request_count > settings.RATE_LIMIT_REQUESTS:
            # Agar limitdan oshib ketgan bo'lsa, foydalanuvchiga ogohlantirish beramiz
            await event.answer("⚠️ Iltimos, xabarlarni juda tez yubormang! Biroz kuting.")
            return
            
        return await handler(event, data)
      
