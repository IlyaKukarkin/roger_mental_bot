import os
from aiogram import Bot, types

token_bot = os.getenv("TOKEN_ROGER_PROD_BOT")
bot = Bot(token=token_bot)

async def delete_keyboard (chat_id: int, message_id: int):
    try:
        await bot.edit_message_reply_markup(chat_id = chat_id, message_id = message_id, reply_markup = None)
    except(Exception):
        return