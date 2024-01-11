"""Module for rate message handler."""

from aiogram import types
from pymongo.errors import PyMongoError

from db.rate import insert_new_rate
from db.user_messages import get_user_message_by_tg_message
from variables import botClient
from common import delete_keyboard
from amplitude_utils import amplitude_send_default_source_event


async def rate_message(callback_query: types.CallbackQuery, rate: bool):
    """
    Handler for rate message callback

    Parameters:
    callback_query (TG Callback): callback to handle
    rate (bool): rate to write in DB

    Returns:
    None
    """

    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)

    try:
        message_to_update = get_user_message_by_tg_message(
            callback_query.message.message_id)

        print("\n")
        print("RATE -> ты оценил сообщение")
        print(message_to_update)
        print(rate)

        insert_new_rate(
            message_to_update["id_user"],
            message_to_update["id_message"],
            rate,
        )
        print("written")
        await callback_query.answer("Спасибо за оценку ❤️")
    except PyMongoError:
        await botClient.send_message(
            callback_query.from_user.id,
            (
                "Ой, кажется, что-то пошло не так 😞 \n"
                "Повтори действие через несколько минут или "
                "напиши разработчикам через команду /feedback"
            )
        )
        await amplitude_send_default_source_event("Error",
                                                  str(callback_query.from_user.id),
                                                  "rate_message",
                                                  "PyMongoError")
