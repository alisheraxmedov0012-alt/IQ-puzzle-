from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple


class AbstractPuzzleEngine(ABC):
    """Barcha puzzle generator va solver motorlari uchun mavhum asosiy klass."""

    @abstractmethod
    def generate(self, difficulty: str = "medium") -> Tuple[str, Dict[str, Any], str]:
        """
        Yangi puzzle konfiguratsiyasini yaratadi.
        
        Returns:
            Tuple[str, Dict[str, Any], str]: 
                - puzzle_hash: unikal identifikator (takrorlanishni oldini olish uchun)
                - engine_data: o'yinning ichki koordinatalari yoki strukturasi
                - correct_answer: to'g'ri javob string ko'rinishida
        """
        pass

    @abstractmethod
    def validate_answer(self, engine_data: Dict[str, Any], user_answer: str, correct_answer: str) -> bool:
        """Foydalanuvchi javobini tekshiradi."""
        pass
      
