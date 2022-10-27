from aiogram import types

from singleton import Bot

async def version_handler(message: types.Message):
    bot = Bot().get_bot()

    await bot.send_message(message.chat.id, "Версия бота Джимми: 0.3.1")
