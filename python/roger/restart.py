from aiogram import types
import requests

from variables import botClient, ROGER_GITHUB_RESTART_TOKEN
from database import get_database


async def restart_command(message: types.Message):
    collection_name = get_database()
    user = collection_name["users"].find_one({"telegram_id": str(message.chat.id)}, {
                                             '_id': 1, "form_id": 1, "is_admin": 1})

    if (not user["is_admin"]):
        await botClient.send_message(message.chat.id, "Сорри, ты не админ этого бота. Не расстраивайся, ты же клиент!")
        return

    await botClient.send_message(message.chat.id, "Рестартую ботов, не писяй!")

    try:
        res = requests.post("https://api.github.com/repos/IlyaKukarkin/roger_mental_bot/actions/workflows/restart.yaml/dispatches",
                            json={'ref': 'main'}, headers={'Authorization': f"Bearer {ROGER_GITHUB_RESTART_TOKEN}"}, timeout=10)

        if (res.status_code != 204):
            await botClient.send_message(message.chat.id, "Писяй!! Что-то пошло не так")
    except (Exception):
        await botClient.send_message(message.chat.id, "Писяй!! Что-то пошло не так")

    collection_name['users'].find().close()
