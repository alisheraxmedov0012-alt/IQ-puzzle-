import enum
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, Enum, Integer, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base, TimestampMixin


class PuzzleType(str, enum.Enum):
    MATCHSTICK = "matchstick"
    IQ_MATRIX = "iq_matrix"
    SHAPE_COUNT = "shape_count"


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    SOLVED = "solved"
    FAILED = "failed"
    TIMEOUT = "timeout"


class Puzzle(Base, TimestampMixin):
    __tablename__ = "puzzles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    puzzle_type: Mapped[PuzzleType] = mapped_column(Enum(PuzzleType), index=True)
    
    # Engine tomonidan yaratilgan unikal konfiguratsiya (masalan, "6+4=4") hoshi qidiruvni tezlashtiradi
    hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    
    # Engine'ga tegishli murakkab ma'lumotlar strukturasi (koordinatalar, matritsa elementlari)
    engine_data: Mapped[Dict[str, Any]] = mapped_column(JSON)
    
    # To'g'ri javob matn yoki kalit ko'rinishida
    correct_answer: Mapped[str] = mapped_column(String(255))
    
    # S3 yoki lokal serverdagi tayyor rasm yo'li
    image_path: Mapped[str] = mapped_column(String(512))

    # Munosabatlar
    sessions: Mapped[list["PuzzleSession"]] = relationship(back_populates="puzzle", cascade="all, delete-orphan")


class PuzzleSession(Base, TimestampMixin):
    __tablename__ = "puzzle_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    puzzle_id: Mapped[int] = mapped_column(Integer, ForeignKey("puzzles.id", ondelete="CASCADE"), index=True)
    
    status: Mapped[SessionStatus] = mapped_column(Enum(SessionStatus), default=SessionStatus.ACTIVE)
    attempts: Mapped[int] = mapped_column(default=0)
    max_attempts: Mapped[int] = mapped_column(default=3)
    
    # Foydalanuvchi yuborgan oxirgi javob
    provided_answer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Sarflangan vaqt (soniyalarda) - status o'zgarganda hisoblanadi
    solve_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Munosabatlar
    user: Mapped["User"] = relationship(back_populates="sessions")
    puzzle: Mapped["Puzzle"] = relationship(back_populates="sessions")
  
