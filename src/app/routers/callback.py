from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.routers.states import SettingsState

router = Router()

@router.callback_query(F.data.startswith('change:'))
async def settings_change(callback: CallbackQuery, state: FSMContext):
    arg = callback.data.split(':')[1]

    if arg == 'delay':
        await callback.message.answer('Enter new delay (sec)')
        await state.set_state(SettingsState.waiting_delay)

    elif arg == 'url':
        await callback.message.answer('Enter new url')
        await state.set_state(SettingsState.waiting_url)
    
    elif arg == 'chat_id':
        await callback.message.answer('Enter new chat_id')
        await state.set_state(SettingsState.waiting_chat_id)
    
    elif arg == 'dataindex':
        await callback.message.answer('Enter new dataindex')
        await state.set_state(SettingsState.waiting_dataindex)

    elif arg == 'status':
        await callback.message.answer('Enter new status sender (true or false)')
        await state.set_state(SettingsState.waiting_status)