from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from database.models.user import User
from database.repositories.user_repository import UserRepository
from telegram.keyboards.menu_keyboards import get_main_menu_keyboard

# Fayllararo import adashmasligi uchun holatlarni shu yerning o'zida e'lon qildik
from aiogram.fsm.state import State, StatesGroup

class PuzzleStates(StatesGroup):
    main_menu = State()
    selecting_type = State()
    solving_puzzle = State()

command_router = Router(name="commands")

@command_router.message(CommandStart())
async def cmd_start(message: types.Message, user_repo: UserRepository, state: FSMContext):
    """Botga start berilganda ishlovchi handler (Idempotent: foydalanuvchi bor bo'lsa qayta yaratmaydi)"""
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
        f"Salom, {message.from_user.first_name}! 👋\n"
        f"**PuzzleForge** platformasiga xush kelibsiz!\n\n"
        f"Bu yerda siz o'z mantiqiy fikrlashingiz va IQ darajangizni sinab ko'rishingiz mumkin.",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="MarkdownV2"
    )
    
