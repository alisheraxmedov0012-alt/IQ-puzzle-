import random
import hashlib
from typing import Dict, Any, Tuple
from engines.base import AbstractPuzzleEngine

class MatchstickEngine(AbstractPuzzleEngine):
    """Gugurt donalari bilan mantiqiy/matematik o'yinlar generatori."""
    
    # 7-segmentli raqamlar xaritasi: 1 - gugurt bor, 0 - yo'q
    # [top, top_left, top_right, middle, bottom_left, bottom_right, bottom]
    SEGMENTS: Dict[int, Tuple[int, ...]] = {
        0: (1, 1, 1, 0, 1, 1, 1),
        1: (0, 0, 1, 0, 0, 1, 0),
        2: (1, 0, 1, 1, 1, 0, 1),
        3: (1, 0, 1, 1, 0, 1, 1),
        4: (0, 1, 1, 1, 0, 1, 0),
        5: (1, 1, 0, 1, 0, 1, 1),
        6: (1, 1, 0, 1, 1, 1, 1),
        7: (1, 0, 1, 0, 0, 1, 0),
        8: (1, 1, 1, 1, 1, 1, 1),
        9: (1, 1, 1, 1, 0, 1, 1),
    }

    def generate(self, difficulty: str = "medium") -> Tuple[str, Dict[str, Any], str]:
        """
        Dinamik ravishda noto'g'ri tenglama yaratadi: A + B = C (Lekin aslida xato).
        To'g'ri javob uchun 1 ta gugurtni ko'chirish talab etiladi.
        """
        # Soddalik uchun tayyor shablonlar bazasidan foydalanamiz yoki algoritmik yaratamiz
        # Haqiqiy ishlab chiqarishda algoritmik transformatsiya qilinadi:
        # Masalan: "6 + 4 = 4" (Xato) -> 1 ta donani 6 dan olib 4 ga qo'shsak: "5 + 4 = 9" (To'g'ri)
        
        equation_pool = [
            {"equation": "6 + 4 = 4", "solution": "5 + 4 = 9", "moves": 1},
            {"equation": "8 - 3 = 11", "solution": "8 + 3 = 11", "moves": 1},
            {"equation": "9 + 3 = 5", "solution": "8 + 3 = 11", "moves": 1},
            {"equation": "5 + 7 = 2", "solution": "5 - 3 = 2", "moves": 1}
        ]
        
        selected = random.choice(equation_pool)
        eq_text = selected["equation"]
        sol_text = selected["solution"]
        
        # Unikal xesh yaratish
        puzzle_hash = hashlib.sha256(eq_text.encode('utf-8')).hexdigest()
        
        engine_data = {
            "display_text": eq_text,
            "moves_required": selected["moves"],
            "segments_representation": [self._text_to_segments(eq_text)]
        }
        
        return puzzle_hash, engine_data, sol_text

    def validate_answer(self, engine_data: Dict[str, Any], user_answer: str, correct_answer: str) -> bool:
        # Bo'shliqlarni olib tashlab solishtiramiz
        clean_user = user_answer.replace(" ", "")
        clean_correct = correct_answer.replace(" ", "")
        return clean_user == clean_correct

    def _text_to_segments(self, text: str) -> list:
        # Matnni segmentlar koordinatasiga o'tkazish (Renderer uchun)
        res = []
        for char in text:
            if char.isdigit():
                res.append({"char": char, "segments": self.SEGMENTS[int(char)]})
            else:
                res.append({"char": char, "segments": None})  # +, -, = belgilari uchun
        return res
      
