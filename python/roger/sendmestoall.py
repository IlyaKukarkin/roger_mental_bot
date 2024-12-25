"""Module providing handlers for "Send message to all" command."""

from typing import Callable
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, MessageError

from states import Recording
from variables import botClient
from db.users import (
    get_user_by_telegram_id,
    update_user_is_active,
    get_count_all_active_users,
    get_all_active_users_partially
)


async def get_message_to_all(message: types.Message):
    """
    Message handler for /sendmestoall command

    Parameters:
    message (TG Message): message to handle

    Returns:
    None
    """

    await Recording.AwaitForAMessageForAll.set()
    await botClient.send_message(
        message.chat.id,
        "Отправь любое сообщение (текст) — и я перешлю его всем пользователям. Отменить: /stop"
    )


async def send_message_to_all(message: types.Message, state: FSMContext):
    """
    Message handler for /sendmestoall command -> "AwaitForAMessageForAll" state

    Parameters:
    message (TG Message): message to handle
    state (TG State): current state

    Returns:
    None
    """

    await state.update_data(name=message.text)

    if message.text == "/stop":
        await state.finish()
        await botClient.send_message(message.chat.id, "Дропнул стейт, отправлять ничего не буду")
        return

    admin_user = get_user_by_telegram_id(str(message.chat.id))

    if not admin_user["is_admin"]:
        await botClient.send_message(
            message.chat.id,
            "Сорри, ты не админ этого бота. Не расстраивайся, ты же пользователь!"
        )
        await state.finish()
        return

    # Do we need this? Not sure atm
    await state.finish()

    count_received_messages, count_bot_blocked, count_other_exceptions = await sending_function(
        lambda _: message.text
    )

    await botClient.send_message(
        message.chat.id,
        (
            "Сообщение доставлено " + str(count_received_messages) +
            " пользователям. Бот заблокирован: " + str(count_bot_blocked) +
            ". Прочие ошибки: " + str(count_other_exceptions)
        )
    )


async def sending_function(get_message: Callable[[int], str]):
    """
    Function to send message to all users

    Parameters:
    get_message (function): function to get message

    Returns:
    None
    """

    limit = 10
    skip = 0

    count_all_active_users = get_count_all_active_users()

    count_received_messages = 0
    count_bot_blocked = 0
    count_other_exceptions = 0

    for _ in range(int(count_all_active_users // limit) +
                   (count_all_active_users % limit > 0)):

        users = get_all_active_users_partially(skip, limit)
        skip += limit

        for user in users:
            try:
                await botClient.send_message(
                    int(user["telegram_id"]),
                    get_message(user["_id"]),
                    disable_web_page_preview=True
                )

                print(user["telegram_id"])
                count_received_messages += 1

            except (BotBlocked, ChatNotFound):  # если юзер заблочил бота, не падаем
                print("Юзер " + user["telegram_id"] + " пидор, заблочил бота")
                update_user_is_active(user['_id'], False)
                count_bot_blocked += 1

            except MessageError as e:
                print(
                    "Failed to send a message to a user " +
                    user['telegram_id'])
                print(e)
                count_other_exceptions += 1

            # pylint: disable=broad-exception-caught
            except Exception as exc:
                print(
                    "Failed to send a message to a user " +
                    user['telegram_id'])
                print(exc)
                count_other_exceptions += 1

    return [count_received_messages, count_bot_blocked, count_other_exceptions]
