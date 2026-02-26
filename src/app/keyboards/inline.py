from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def main_settings():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='Change Delay', callback_data='change:delay'))
    builder.add(InlineKeyboardButton(text='Change URL', callback_data='change:url'))
    builder.add(InlineKeyboardButton(text='Change GROUP_CHAT_ID', callback_data='change:chat_id'))
    builder.add(InlineKeyboardButton(text='Change CURRENT_DATAINDEX', callback_data='change:dataindex'))

    return builder.adjust(1).as_markup()