from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from database.models.puzzle import PuzzleType
from telegram.keyboards.menu_keyboards import get_puzzle_type_keyboard, get_main_menu_keyboard
from telegram.states import PuzzleStates
from services.puzzle_service import PuzzleService

game_router = Router(name="game")


@game_router.message(F.text == "🧩 Yangi Puzzle Boshlash", PuzzleStates.main_menu)
async def choose_puzzle_type(message: types.Message, state: FSMContext) -> None:
    """O'yin turlari menyusini chiqarish."""
    await state.set_state(PuzzleStates.selecting_type)
    await message.answer("Qaysi turdagi mantiqiy puzzleni yechmoqchisiz? Tanlang:", reply_markup=get_puzzle_type_keyboard())


@game_router.callback_query(F.data.startswith("play:"), PuzzleStates.selecting_type)
async def start_puzzle_session(callback: types.CallbackQuery, puzzle_service: PuzzleService, state: FSMContext) -> None:
    """Tanlangan o'yin turi bo'yicha puzzle generatsiya qilib, foydalanuvchiga yuborish."""
    await callback.answer()
    
    puzzle_type_str = callback.data.split(":")[1]
    puzzle_type = PuzzleType(puzzle_type_str)
    
    # Servis orqali yangi yoki mavjud faol o'yinni olamiz
    puzzle, session = await puzzle_service.get_or_create_active_puzzle(callback.from_user.id, puzzle_type)
    
    # FSM holatni "Javob berish" rejimiga o'tkazamiz
    await state.set_state(PuzzleStates.solving_puzzle)
    
    # Rasmni tayyorlab Telegram orqali yuboramiz
    photo = FSInputFile(puzzle.image_path)
    
    await callback.message.answer_photo(
        photo=photo,
        caption=(
            f"🎯 **Yangi topshiriq\!**\n\n"
            f"💡 Turi: `{puzzle_type.value.upper()}`\n"
            f"⚠️ Sizda jami **{session.max_attempts} ta** urinish bor\.\n\n"
            f"📝 Javobingizni quyida matn ko'rinishida yozib yuboring\:"
        ),
        parse_mode="MarkdownV2"
    )
    # Eski callback xabarini o'chirib tashlaymiz
    await callback.message.delete()


@game_router.message(PuzzleStates.solving_puzzle)
async def process_puzzle_answer(message: types.Message, puzzle_service: PuzzleService, state: FSMContext) -> None:
    """Foydalanuvchi javobini qabul qilib tekshirish."""
    user_id = message.from_user.id
    user_answer = message.text.strip()
    
    # Servis orqali javobni tekshiramiz
    is_correct, session = await puzzle_service.check_user_answer(user_id, user_answer)
    
    if is_correct:
        await message.answer(
            f"🎉 **Tabriklaymiz\! To'g'ri javob\!**\n"
            f"⏱ Sarflangan vaqt: `{session.solve_time}` soniya\.\n"
            f"🔢 Urinishlar soni: `{session.attempts}` ta\.",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="MarkdownV2"
        )
        await state.set_state(PuzzleStates.main_menu)
        
    else:
        if session.status.value == "failed":
            await message.answer(
                f"❌ **Afsuski, barcha urinishlaringiz tugadi\!**\n"
                f"O'yin yakunlandi\. Keyingi safar albatta omadingiz keladi\!",
                reply_markup=get_main_menu_keyboard(),
                parse_mode="MarkdownV2"
            )
            await state.set_state(PuzzleStates.main_menu)
        else:
            await message.answer(
                f"❌ **Noto'g'ri javob\!**\n"
                f"Qayta urinib ko'ring\. Sizda yana **{session.max_attempts - session.attempts} ta** imkoniyat bor\.",
                parse_mode="MarkdownV2"
            )
          
