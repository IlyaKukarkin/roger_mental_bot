"""Module providing handlers for "Send new year message to all active users" command."""

from datetime import datetime

from variables import botClient
from sendmestoall import sending_function
from db.users import (
    get_user_by_telegram_id,
)

# Add timeout for sending messages
# Maybe 10 messages, then 15 seconds sleep


async def send_new_year_message(telegram_id: str):
    """
    Message handler for /sendnewyearmessage command

    Parameters:
    Telegram_id (int): Telegram ID of the user who requested the command

    Returns:
    None
    """

    admin_user = get_user_by_telegram_id(telegram_id)

    if not admin_user["is_admin"]:
        await botClient.send_message(
            telegram_id,
            "Сорри, ты не админ этого бота. Не расстраивайся, ты же пользователь!"
        )
        return

    count_received_messages, count_bot_blocked, count_other_exceptions = await sending_function(
        get_new_year_message
    )

    await botClient.send_message(
        telegram_id,
        (
            "Сообщение доставлено " + str(count_received_messages) +
            " пользователям. Бот заблокирован: " + str(count_bot_blocked) +
            ". Прочие ошибки: " + str(count_other_exceptions)
        )
    )


def get_new_year_message(user_id: int):
    """
    Get new year message for a user

    Parameters:
    user_id (int): user ID

    Returns:
    str: new year message
    """

    link = "https://rogerbot.app/2025/" + str(user_id)
    current_year = datetime.now().year

    return f"""
    Привет, друг! 💙

Я подготовил статистику по твоему настроению в уходящем {current_year} году. Переходи по ссылке и узнай, каким цветом можно описать твой год, а еще сколько человек стали счастливее благодаря твоей поддержке.

Твоя статистика доступна по ссылке {link}

А если тебе нравится пользоваться Роджером, поделись своей статистикой в соцсетях! Тогда еще больше людей смогут следить за своим настроением вместе со мной 😌

С наступающим Новым годом! Надеюсь, твой следующий год будет только в 🟢 цветах.

Твой новогодний Роджер 🎄
    """
