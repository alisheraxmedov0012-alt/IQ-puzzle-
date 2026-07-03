from typing import Any, Dict, Optional

class PuzzleForgeException(Exception):
    """Barcha ichki xatoliklar uchun asosiy klass."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

class DomainException(PuzzleForgeException):
    """Biznes logika qatlamida yuz beradigan xatoliklar."""
    pass

class DatabaseException(PuzzleForgeException):
    """Ma'lumotlar bazasi bilan ishlashda yuz beradigan xatoliklar."""
    pass

class EntityNotFoundException(DomainException):
    """So'ralgan ob'ekt bazadan topilmaganda."""
    def __init__(self, entity_name: str, identifier: Any):
        super().__init__(
            message=f"{entity_name} topilmadi: {identifier}", 
            code="ENTITY_NOT_FOUND"
        )

class RateLimitException(PuzzleForgeException):
    """Foydalanuvchi limitdan ko'p so'rov yuborganda."""
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(
            message=f"Ko'p so'rov yuborildi. Iltimos {retry_after} soniya kuting.", 
            code="RATE_LIMIT_EXCEEDED"
        )
      
