from aiogram.fsm.state import State, StatesGroup


class PuzzleStates(StatesGroup):
    """Puzzle platformasining asosiy FSM holatlari."""
    main_menu = State()          # Asosiy menyuda turgandagi holat
    selecting_type = State()     # O'yin turini tanlash jarayoni
    solving_puzzle = State()     # Faol puzzle yechilayotgan xavfsiz jarayon
  
