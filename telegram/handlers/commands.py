from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from database.models.user import User
from database.repositories.user_repository import UserRepository
from telegram.keyboards.menu_keyboards import get_main_menu_keyboard
from app.telegram.puzzle_states import PuzzleStates

command_router = Router(name="commands")


@command_router.message(CommandStart())
async def cmd_start(message: types.Message, user_repo: UserRepository, state: FSMContext) -> None:
    """Botga start berilganda ishlovchi handler (Idempotent: foydalanuvchi qayta start bossa duplicate bo'lmaydi)."""
    user_id = message.from_user.id
    
    # 1. Foydalanuvchi bazada borligini tekshiramiz
    user = await user_repo.get(user_id)
    if not user:
        # Yangi foydalanuvchi ob'ektini yaratamiz
        new_user = User(
            id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code or "uz"
        )
        await user_repo.create_user_with_stats(new_user)
    
    # Holatni asosiy menyuga o'tkazamiz
    await state.set_state(PuzzleStates.main_menu)
    
    await message.answer(
        f"Salom, *{message.from_user.first_name}*\! 👋\n"
        f"**PuzzleForge** platformasiga xush kelibsiz\.\n"
        f"Bu yerda siz o'z mantiqiy fikrlashingiz va IQ darajangizni sinab ko'rishingiz mumkin\. 🎉",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="MarkdownV2"
    )
  
