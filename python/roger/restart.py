from aiogram import types
import requests

from config import bot, github_restart_token
from database import get_database


async def restart_command(message: types.Message):
    collection_name = get_database()
    user = collection_name["users"].find_one({"telegram_id": str(message.chat.id)}, {
                                             '_id': 1, "form_id": 1, "is_admin": 1})

    if (user["is_admin"] == False):
        await bot.send_message(message.chat.id, "Сорри, ты не админ этого бота. Не расстраивайся, ты же клиент!")
        return

    await bot.send_message(message.chat.id, "Рестартую ботов, не писяй!")

    try:
        res = requests.post("https://api.github.com/repos/IlyaKukarkin/roger_mental_bot/actions/workflows/restart.yaml/dispatches",
                      json={'ref': 'main'}, headers={'Authorization': f"Bearer {github_restart_token}"})
        
        if (res.status_code != 204):
            await bot.send_message(message.chat.id, "Писяй!! Что-то пошло не так")
    except (Exception):
        await bot.send_message(message.chat.id, "Писяй!! Что-то пошло не так")

    collection_name['users'].find().close()
