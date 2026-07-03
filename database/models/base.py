from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Barcha ma'lumotlar bazasi modellari uchun asosiy deklarativ klass."""
    pass


class TimestampMixin:
    """Yaratilgan va yangilangan vaqtlarni avtomatlashtiruvchi mixin."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        sort_order=998
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        sort_order=999
    )
  
