from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from singleton import Bot

ask_for_rate_good = InlineKeyboardButton('✅', callback_data='rate_good')
ask_for_rate_bad = InlineKeyboardButton('❌', callback_data='rate_bad')
ask_for_rate_messages = InlineKeyboardMarkup().add(
    ask_for_rate_good, ask_for_rate_bad)


async def delete_keyboard(chat_id: int, message_id: int):
    bot = Bot().get_bot()

    try:
        await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
    except (Exception):
        return
