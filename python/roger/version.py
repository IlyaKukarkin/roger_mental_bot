"""Module providing functions for /version command."""

from aiogram import types

from variables import botClient


async def version_command(message: types.Message, version: str):
    """
    Message handler for /version command

    Parameters:
    message (TG Message): message to handle
    version (str): current version of Roger bot

    Returns:
    None
    """

    await botClient.send_message(message.chat.id, "Версия бота Роджер: " + version)
