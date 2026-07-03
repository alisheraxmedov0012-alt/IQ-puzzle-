from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from core.logger import logger
from core.exceptions import EntityNotFoundException, DomainException
from database.models.puzzle import Puzzle, PuzzleSession, PuzzleType, SessionStatus
from database.models.user import User
from database.repositories.puzzle_repository import PuzzleRepository, PuzzleSessionRepository
from database.repositories.user_repository import UserRepository
from engines.matchstick.generator import MatchstickEngine
from engines.iq.generator import IQMatrixEngine
from engines.renderer.image_renderer import ImageRenderingEngine


class PuzzleService:
    """Tizimdagi o'yin jarayonlari va biznes logikalarini boshqaruvchi asosiy servis."""

    def __init__(
        self,
        user_repo: UserRepository,
        puzzle_repo: PuzzleRepository,
        session_repo: PuzzleSessionRepository,
        renderer: ImageRenderingEngine
    ):
        self.user_repo = user_repo
        self.puzzle_repo = puzzle_repo
        self.session_repo = session_repo
        self.renderer = renderer
        
        # O'yin dvigatellari xaritasi (Strategy Pattern)
        self.engines = {
            PuzzleType.MATCHSTICK: MatchstickEngine(),
            PuzzleType.GRID_IQ: IQMatrixEngine()  # IQ matrix nomlanishiga moslab
        }

    async def get_or_create_active_puzzle(self, user_id: int, puzzle_type: PuzzleType) -> Tuple[Puzzle, PuzzleSession]:
        """Foydalanuvchining faol seansini qaytaradi yoki yangi puzzle generatsiya qilib beradi."""
        # 1. Avval faol seans borligini tekshiramiz
        active_session = await self.session_repo.get_active_session(user_id)
        if active_session:
            return active_session.puzzle, active_session

        # 2. Mos keluvchi dvigatelni tanlaymiz
        engine = self.engines.get(puzzle_type)
        if not engine:
            raise DomainException(f"Bunday puzzle turi qo'llab-quvvatlanmaydi: {puzzle_type}")

        # 3. Dvigateldan yangi puzzle konfiguratsiyasini olamiz
        puzzle_hash, engine_data, correct_answer = engine.generate(difficulty="medium")

        # 4. Bazada bu shablon avval yaratilganmi (kesh)?
        puzzle = await self.puzzle_repo.get_by_hash(puzzle_hash)
        if not puzzle:
            # Rasm render qilamiz
            image_path = await self.renderer.render_puzzle(puzzle_type.value, puzzle_hash, engine_data)
            
            # Yangi puzzle shablonini bazaga yozamiz
            puzzle = Puzzle(
                puzzle_type=puzzle_type,
                hash=puzzle_hash,
                engine_data=engine_data,
                correct_answer=correct_answer,
                image_path=image_path
            )
            puzzle = await self.puzzle_repo.create(puzzle)

        # 5. Yangi o'yin seansini ochamiz
        new_session = PuzzleSession(
            user_id=user_id,
            puzzle_id=puzzle.id,
            status=SessionStatus.ACTIVE,
            max_attempts=3
        )
        new_session = await self.session_repo.create(new_session)

        logger.info(f"Foydalanuvchi {user_id} uchun yangi puzzle seansi ({new_session.id}) ochildi.")
        return puzzle, new_session

    async def check_user_answer(self, user_id: int, answer: str) -> Tuple[bool, PuzzleSession]:
        """Foydalanuvchi yuborgan javobni tekshiradi va natijaga qarab seans holatini yangilaydi."""
        # 1. Faol seansni topamiz
        session = await self.session_repo.get_active_session(user_id)
        if not session:
            raise DomainException("Sizda faol puzzle seansi mavjud emas. Avval o'yinni boshlang.")

        puzzle = session.puzzle
        engine = self.engines.get(puzzle.puzzle_type)
        
        # 2. Vaqtni va urinishlarni hisoblaymiz
        session.attempts += 1
        session.provided_answer = answer
        
        now = datetime.utcnow()
        # Soddalik uchun created_at bilan solishtiramiz
        solve_time_seconds = int((now - session.created_at.replace(tzinfo=None)).total_seconds())
        session.solve_time = solve_time_seconds

        # 3. Javobni validatsiya qilamiz
        is_correct = engine.validate_answer(puzzle.engine_data, answer, puzzle.correct_answer)

        if is_correct:
            session.status = SessionStatus.SOLVED
            logger.info(f"User {user_id} puzzleni to'g'ri yechdi. Seans ID: {session.id}")
        else:
            if session.attempts >= session.max_attempts:
                session.status = SessionStatus.FAILED
                logger.info(f"User {user_id} barcha urinishlardan yutqazdi. Seans ID: {session.id}")
            else:
                session.status = SessionStatus.ACTIVE  # Hali imkoniyati bor

        # O'zgarishlarni yangilaymiz
        update_data = {
            "attempts": session.attempts,
            "provided_answer": session.provided_answer,
            "solve_time": session.solve_time,
            "status": session.status
        }
        await self.session_repo.update(session, update_data)
        
        return is_correct, session
      
