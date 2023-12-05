"""Module providing handlers for "Restart Bots" command."""

from aiogram import types
import requests
from requests.exceptions import RequestException

from variables import botClient, ROGER_GITHUB_RESTART_TOKEN
from db.users import get_user_by_telegram_id


async def restart_command(message: types.Message):
    """
    Message handler for /restart command

    Parameters:
    message (TG Message): message to handle

    Returns:
    None
    """

    # pylint: disable=duplicate-code
    user = get_user_by_telegram_id(str(message.chat.id))

    if not user["is_admin"]:
        await botClient.send_message(
            message.chat.id,
            "Сорри, ты не админ этого бота. Не расстраивайся, ты же клиент!"
        )
        return

    await botClient.send_message(message.chat.id, "Рестартую ботов, не писяй!")

    try:
        res = requests.post(
            (
                "https://api.github.com/repos/IlyaKukarkin/roger_mental_bot" +
                "/actions/workflows/restart.yaml/dispatches"
            ),
            json={'ref': 'main'},
            headers={'Authorization': f"Bearer {ROGER_GITHUB_RESTART_TOKEN}"},
            timeout=10
        )

        if res.status_code != 204:
            await botClient.send_message(message.chat.id, "Писяй!! Что-то пошло не так")
    except RequestException:
        await botClient.send_message(message.chat.id, "Писяй!! Что-то пошло не так")
