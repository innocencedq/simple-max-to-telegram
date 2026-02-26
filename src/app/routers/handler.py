from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.routers.states import SettingsState
from app.keyboards.inline import main_settings
from app.checker import get_last_message, forced_message
from config import config, update_env

router = Router()

@router.message(Command('help'))
async def help_command(message: Message):
    await message.reply('Commands:\n\n/help\n/whoami\n/settings\n/getlastmessage\n/forcemessage')


@router.message(Command('getlastmessage'))
async def getlastmessage_command(message: Message):
    await message.reply('requesting...')

    await get_last_message()


@router.message(Command('settings'))
async def settings_command(message: Message):
    await message.reply(f'<b>Settings</b>\n\nDelay requesting: {config.DELAY_REQUESTING} sec ({int(config.DELAY_REQUESTING) // 60} mins)\nURL: {config.URL}\nGROUP_CHAT_ID: {config.GROUP_CHAT_ID}\nCURRENT_DATAINDEX: {config.CURRENT_DATAINDEX}\nCurrent Status: {config.STATUS_REQUSTING}',
                        reply_markup=await main_settings(),
                        parse_mode='html')


@router.message(Command('forcemessage'))
async def getlastmessage_command(message: Message):
    await message.reply('requesting...')

    await forced_message()


@router.message(SettingsState.waiting_delay)
async def update_delay(message: Message, state: FSMContext):
    params = message.text

    update_env('DELAY_REQUESTING', params)

    await state.clear()
    await settings_command(message)


@router.message(SettingsState.waiting_chat_id)
async def update_delay(message: Message, state: FSMContext):
    params = message.text

    update_env('GROUP_CHAT_ID', str(params))

    print(params)

    await state.clear()
    await settings_command(message)


@router.message(SettingsState.waiting_dataindex)
async def update_delay(message: Message, state: FSMContext):
    params = message.text

    update_env('CURRENT_DATAINDEX', params)

    await state.clear()
    await settings_command(message)


@router.message(SettingsState.waiting_url)
async def update_delay(message: Message, state: FSMContext):
    params = message.text

    update_env('URL', str(params))

    await state.clear()
    await settings_command(message)


@router.message(SettingsState.waiting_status)
async def update_delay(message: Message, state: FSMContext):
    params = message.text

    if params.lower() == 'true':
        update_env('STATUS_REQUSTING', 'active')
    elif params.lower() == 'false':
        update_env('STATUS_REQUSTING', 'deactivated')

    await state.clear()
    await settings_command(message)


@router.message(Command('whoami'))
async def cmd_whoami(message: Message):
    chat = message.chat
    
    await message.reply(f'GROUP CHAT ID: `{chat.id}`', parse_mode="Markdown")


@router.message(Command('clear'))
async def cmd_clear(message: Message, state: FSMContext):
    await state.clear()
    await message.reply('all states clear!')