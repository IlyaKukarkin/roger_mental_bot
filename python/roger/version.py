from aiogram import types

from variables import botClient


async def version_command(message: types.Message, version: str):
    await botClient.send_message(message.chat.id, "Версия бота Роджер: " + version)
