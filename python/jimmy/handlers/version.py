from aiogram import types
# import requests
# import time
# import json

from singleton import Bot
# from db.messages import Messages

async def version_handler(message: types.Message):
    bot = Bot().get_bot()
    await bot.send_message(message.chat.id, "Версия бота Джимми: 1.0.1")
