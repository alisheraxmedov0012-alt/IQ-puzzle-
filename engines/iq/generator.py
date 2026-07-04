import random
import hashlib
from typing import Dict, Any, Tuple, List
from engines.base import AbstractPuzzleEngine

class IQMatrixEngine(AbstractPuzzleEngine):
    """Mantiqiy IQ matritsalar (Matrix Puzzles) generatori."""

    def generate(self, difficulty: str = "medium") -> Tuple[str, Dict[str, Any], str]:
        """
        3x3 matritsa yaratadi. Qonuniyat: Har bir katak ichidagi shakllar soni
        qator bo'ylab o'sib boradi: Qator1: 1, 2, 3 | Qator2: 2, 3, 4 | Qator3: 3, 4, [5]
        """
        # Qonuniyat asosi: boshlang'ich shakllar soni matritsasi
        base_matrix = [
            [1, 2, 3],
            [2, 3, 4],
            [3, 4, 5]  # Javob: 5 bo'lishi kerak
        ]

        # Variantlar generatsiyasi
        correct_answer = "5"
        options = ["3", "4", "5", "6", "7"]
        random.shuffle(options)

        # Unikal konfiguratsiya xeshi
        matrix_id = f"matrix_seq_{random.randint(1000, 9999)}"
        puzzle_hash = hashlib.sha256(matrix_id.encode('utf-8')).hexdigest()

        engine_data = {
            "matrix_type": "shape_count_progression",
            "grid_size": 3,
            "matrix_values": [
                [1, 2, 3],
                [2, 3, 4],
                [3, 4, "?"]
            ],
            "options": options,
            "shape_style": random.choice(["circle", "square", "triangle"])
        }

        return puzzle_hash, engine_data, correct_answer

    def validate_answer(self, engine_data: Dict[str, Any], user_answer: str, correct_answer: str) -> bool:
        return user_answer.strip() == correct_answer.strip()
        
