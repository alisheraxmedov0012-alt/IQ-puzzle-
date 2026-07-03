import asyncio
from pathlib import Path
from typing import List
from PIL import Image
from core.logger import logger


class PDFExporter:
    """Generatsiya qilingan rasmlarni yagona PDF hujjatiga jamlovchi eksport dvigateli."""

    def __init__(self, export_dir: str = "storage/exports"):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    async def create_puzzle_book(self, session_id: int, image_paths: List[str]) -> str:
        """Rasmlar ro'yxatini asinxron tarzda bitta PDF fayliga o'tkazadi."""
        return await asyncio.to_thread(self._export_sync, session_id, image_paths)

    def _export_sync(self, session_id: int, image_paths: List[str]) -> str:
        if not image_paths:
            raise ValueError("Eksport qilish uchun rasmlar berilmadi.")

        pdf_path = self.export_dir / f"puzzle_book_{session_id}.pdf"
        
        # Birinchi rasmni ochamiz va qolganlarini unga RGB konvertatsiya qilib qo'shamiz
        images = []
        for path in image_paths:
            if Path(path).exists():
                img = Image.open(path).convert("RGB")
                images.append(img)

        if not images:
            raise FileNotFoundError("Hech qaysi rasm manbasi topilmadi.")

        first_img = images[0]
        first_img.save(
            pdf_path,
            save_all=True,
            append_images=images[1:],
            resolution=100.0,
            quality=85
        )
        
        logger.info(f"PDF Kitobcha muvaffaqiyatli eksport qilindi: {pdf_path}")
        return str(pdf_path)
      
