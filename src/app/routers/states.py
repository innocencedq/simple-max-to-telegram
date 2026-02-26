from aiogram.fsm.state import State, StatesGroup

class SettingsState(StatesGroup):
    waiting_delay = State()
    waiting_chat_id = State()
    waiting_url = State()
    waiting_dataindex = State()
    waiting_status = State()
