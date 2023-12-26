"""Module providing handlers for "Send message to all" command."""

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, MessageError

from states import Recording
from variables import botClient
from db.users import (
    get_user_by_telegram_id,
    get_all_active_users,
    update_user_is_active
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
        "Отправь любое сообщение (текст) — и я перешлю его всем пользователям"
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

    users = get_all_active_users()

    count_received_messages = 0
    count_bot_blocked = 0
    count_other_exceptions = 0

    for user in users:
        try:
            await botClient.send_message(int(user["telegram_id"]), message.text)
            count_received_messages += 1

        except (BotBlocked, ChatNotFound):  # если юзер заблочил бота, не падаем
            print("Юзер " + user["telegram_id"] + " пидор, заблочил бота")
            update_user_is_active(user['_id'], False)
            count_bot_blocked += 1

        except MessageError as e:
            print("Failed to send a message to a user " + user['telegram_id'])
            print(e)
            count_other_exceptions += 1

    await botClient.send_message(
        message.chat.id,
        (
            "Сообщение доставлено " + str(count_received_messages) +
            " пользователям. Бот заблокирован: " + str(count_bot_blocked) +
            ". Прочие ошибки: " + str(count_other_exceptions)
        )
    )


async def send_newyear_message_to_all(message: types.Message):

    """
    Message handler for new year stata command /sendnewyearmestoall

    Parameters:
    message (TG Message): message to handle

    Returns:
    None
    """

    admin_user = get_user_by_telegram_id(str(message.chat.id))

    if not admin_user["is_admin"]:
        await botClient.send_message(
            message.chat.id,
            "Сорри, ты не админ этого бота. Не расстраивайся, ты же пользователь!"
        )
        return

    users = get_all_active_users()

    count_received_messages = 0
    count_bot_blocked = 0
    count_other_exceptions = 0

    link = "https://rogerbot.tech/2023/"

    message_text_part1 = "Привет, друг! 💙" \
        "\n\nКоманда Роджера подготовила твою статистику за 2023 год. " \
        "Переходи по ссылке и узнай, " \
        "каким цветом можно описать твой год, " \
        "а еще сколько человек стали счастливее благодаря твоей поддержке." \
        "\n\nТвоя статистика доступна по ссылке "

    message_text_part2 = "\n\nА если тебе нравится пользоваться Роджером, " \
        "поделись статистикой в соцсетях! " \
        "Тогда еще больше людей смогут следить " \
        "за своим настроением вместе с Роджером 😌" \
        "\n\nС наступающим Новым годом! Загадываем, " \
        "чтобы каждый день следующего года был только 🟢 цвета." \
        "\n\nТвой новогодний Роджер 🎄"

    for user in users:
        try:
            link += str(user["_id"])

            await botClient.send_message(
                int(user["telegram_id"]),
                message_text_part1 + link + message_text_part2,
                disable_web_page_preview=True)

            count_received_messages += 1

        except (BotBlocked, ChatNotFound):  # если юзер заблочил бота, не падаем
            print("Юзер " + user["telegram_id"] + " пидор, заблочил бота")

            update_user_is_active(user['_id'], False)

            count_bot_blocked += 1

        except Exception as e:  # pylint: disable=broad-exception-caught
            print("Failed to send a message to a user " + user['telegram_id'])
            print(e)
            count_other_exceptions += 1

    await botClient.send_message(
        message.chat.id,
        (
            "Сообщение доставлено " + str(count_received_messages) +
            " пользователям. Бот заблокирован: " + str(count_bot_blocked) +
            ". Прочие ошибки: " + str(count_other_exceptions)
        )
    )
