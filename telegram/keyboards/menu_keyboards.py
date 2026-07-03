from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database.models.puzzle import PuzzleType


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu tugmalari."""
    keyboard = [
        [KeyboardButton(text="🧩 Yangi Puzzle Boshlash")],
        [KeyboardButton(text="📊 Mening Statistikam"), KeyboardButton(text="🏆 Global Reyting")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_puzzle_type_keyboard() -> InlineKeyboardMarkup:
    """O'yin turlarini tanlash uchun Inline tugmalar."""
    inline_keyboard = [
        [InlineKeyboardButton(text="🥢 Matchstick (Gugurt donalari)", callback_data=f"play:{PuzzleType.MATCHSTICK.value}")],
        [InlineKeyboardButton(text="🔢 IQ Matrix (Mantiqiy kvadrat)", callback_data=f"play:{PuzzleType.GRID_IQ.value}")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_game")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
  
