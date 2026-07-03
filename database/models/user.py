import enum
from typing import List, Optional
from sqlalchemy import BigInteger, String, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    BANNED = "banned"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    # Telegram user_id katta son bo'lgani uchun BigInteger va primary key qilinadi
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    language_code: Mapped[str] = mapped_column(String(10), default="uz")
    
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), default=UserStatus.ACTIVE)

    # Munosabatlar (Relationships)
    sessions: Mapped[List["PuzzleSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    statistics: Mapped["UserStatistics"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserStatistics(Base, TimestampMixin):
    __tablename__ = "user_statistics"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    puzzles_solved: Mapped[int] = mapped_column(default=0)
    puzzles_failed: Mapped[int] = mapped_column(default=0)
    total_score: Mapped[int] = mapped_column(default=0)
    iq_rating: Mapped[int] = mapped_column(default=100)  # Standart IQ darajasidan boshlanadi
    average_solve_time: Mapped[float] = mapped_column(default=0.0)  # soniyalarda

    # Munosabatlar
    user: Mapped["User"] = relationship(back_populates="statistics")
  
