from aiogram import types
from config import bot

async def version_command (message: types.Message, version: str):
    await bot.send_message(message.chat.id, "Версия бота Роджер: " + version)