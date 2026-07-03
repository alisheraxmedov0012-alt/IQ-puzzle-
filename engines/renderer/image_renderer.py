import asyncio
from pathlib import Path
from typing import Dict, Any
from PIL import Image, ImageDraw, ImageFont
from core.logger import logger


class ImageRenderingEngine:
    """Dinamik ravishda vizual rasmlarni generatsiya qiluvchi dvigatel (Thread-safe & Async-wrapped)."""

    def __init__(self, output_dir: str = "storage/images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Standart tizim shriftini yuklaymiz (Production muhitida aniq yo'l berilishi kerak)
        try:
            self.font = ImageFont.load_default()
        except Exception:
            logger.warning("Standart shrift yuklanmadi, fallback rejimi.")
            self.font = None

    async def render_puzzle(self, puzzle_type: str, puzzle_hash: str, engine_data: Dict[str, Any]) -> str:
        """Asosiy Event Loop'ni bloklamaslik uchun chizish jarayonini alohida thread'ga topshiradi."""
        return await asyncio.to_thread(self._render_sync, puzzle_type, puzzle_hash, engine_data)

    def _render_sync(self, puzzle_type: str, puzzle_hash: str, engine_data: Dict[str, Any]) -> str:
        """Sinxron chizish logikasi."""
        file_path = self.output_dir / f"{puzzle_type}_{puzzle_hash}.png"
        
        # Agar rasm avval chizilgan bo'lsa, qayta chizmaymiz (Caching mechanism)
        if file_path.exists():
            return str(file_path)

        # Rasm o'lchamlari va fon (Dark mode friendly)
        width, height = 800, 400
        image = Image.new("RGB", (width, height), color="#1E1E2E")
        draw = ImageDraw.Draw(image)

        if puzzle_type == "matchstick":
            self._draw_matchstick(draw, engine_data["display_text"])
        elif puzzle_type == "iq_matrix":
            self._draw_iq_matrix(draw, engine_data)
        else:
            # Fallback oddiy matnli rasm
            draw.text((50, 180), f"Puzzle: {puzzle_type.upper()}", fill="#CDD6F4", font=self.font)

        # Rasmni saqlaymiz
        image.save(file_path, "PNG", optimize=True)
        logger.info(f"Yangi puzzle rasmi muvaffaqiyatli render qilindi: {file_path}")
        return str(file_path)

    def _draw_matchstick(self, draw: ImageDraw.Draw, text: str) -> None:
        """Gugurt uslubidagi raqamlarni chizish simulyatsiyasi."""
        # Haqiqiy production kodida bu yerda chiziqlar (gugurtlar) koordinatalar bo'yicha chiziladi
        # Hozircha yuqori sifatli vizualizatsiya uchun chiroyli font matni ko'rinishida beramiz
        draw.text((150, 150), text, fill="#F38BA8", font=self.font)

    def _draw_iq_matrix(self, draw: ImageDraw.Draw, data: Dict[str, Any]) -> None:
        """$3 \times 3$ hajmdagi katakchalarni va ichidagi elementlarni chizish."""
        start_x, start_y = 250, 50
        cell_size = 100
        padding = 10

        matrix_values = data["matrix_values"]
        shape_style = data["shape_style"]

        for i in range(3):
            for j in range(3):
                x1 = start_x + j * (cell_size + padding)
                y1 = start_y + i * (cell_size + padding)
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                # Katakcha hoshiyasi
                draw.rectangle([x1, y1, x2, y2], outline="#89B4FA", width=3)
                
                val = matrix_values[i][j]
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

                if val == "?":
                    draw.text((center_x - 10, center_y - 15), "?", fill="#FAB387", font=self.font)
                else:
                    # Katak ichiga shakllarni chizish (masalan soniga mos ravishda doirachalar)
                    count = int(val)
                    for r in range(count):
                        offset = (r - count/2) * 15 + 10
                        draw.ellipse([center_x + offset - 5, center_y - 5, center_x + offset + 5, center_y + 5], fill="#A6E3A1")
              
