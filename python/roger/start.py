"""Module providing functions for /start command."""

import time
from aiogram import types
from bson import ObjectId

from db.users import get_user_by_telegram_id, update_user_is_active, insert_new_empty_user
from states import Registration
from keyboards import ask_for_name_kb
from variables import botClient, botDispatcher


async def start_command(message: types.Message):
    """
    Message handler for /start command

    Parameters:
    message (TG Message): message to handle

    Returns:
    None
    """

    user = get_user_by_telegram_id(str(message.chat.id))

    if user is None:
        form_id = ObjectId()
        if message.from_user.username is None:
            message.from_user.username = ""
        user_id = insert_new_empty_user(
            message.from_user.username, str(
                message.chat.id), form_id)
        await botClient.send_message(
            message.chat.id,
            "Привет 👋 \n \nЯ Роджер — бот для твоей кукухи."
        )
        time.sleep(1)

        await botClient.send_message(
            message.chat.id,
            "Каждый вечер я буду интересоваться твоим настроением.\n"
            "Я умею распознавать 4 настроения:\n\n"
            "🟢 — день был великолепен, лучше и представить нельзя\n"
            "🟡 — вариант для хорошего дня, в котором были небольшие неприятности\n"
            "🟠 — день мог бы быть сильно лучше, но еще не все потеряно\n"
            "🔴 — день был хуже некуда, тебе срочно нужна поддержка"
        )
        time.sleep(6)

        await botClient.send_message(
            message.chat.id,
            (
                "Если ты выберешь 🟠 и 🔴 настроение, тогда и начнется самое интересное 🙃 \n"
                "Я подберу тебе ободряющее сообщение от другого пользователя, "
                "у которого настроение было отличным — и он захотел поделиться им с тобой"
            )
        )
        time.sleep(5)

        await botClient.send_message(
            message.chat.id,
            (
                "И наоборот — если у тебя выдался 🟢 и 🟡 день, "
                "то ты сможешь написать свое позитивное сообщение.  \n"
                "Когда твое сообщение пройдет модерацию, я буду показывать его тем, "
                "кому это сейчас важно"
            )
        )
        time.sleep(5)

        await botClient.send_message(
            message.chat.id,
            "Вот такая простая магия ✨"
        )
        time.sleep(3)

        await botClient.send_message(
            message.chat.id,
            (
                "Давай познакомимся с тобой поближе! Не переживай — "
                "ты сможешь отредактировать эти данные позднее 🙃"
            )
        )
        time.sleep(2)

        await botClient.send_message(
            message.chat.id,
            (
                "Тебя зовут " + message.from_user.first_name +
                "? Подтверди свое имя или введи другое"
            ),
            reply_markup=ask_for_name_kb
        )

        await Registration.Name.set()
        state = botDispatcher.get_current().current_state()
        await state.update_data(user_id=user_id, source="reg")
        return

    if user["is_active"]:
        await botClient.send_message(
            message.chat.id,
            "Кажется, мы уже знакомы, " + user['name']
        )
        return

    # это последний степ регистрации; если он задан, значит, пользователь уже
    # зарегался
    if hasattr(user, "timezone"):
        await botClient.send_message(
            message.chat.id,
            "Здорово, что ты вернулся, " +
            user['name'] + " 😍\n\nЯ продолжу интересоваться твоим настроением 😌"
        )
        update_user_is_active(user['_id'], True)
        return

    await botClient.send_message(
        message.chat.id,
        "Ты уже начал регистрацию\n\nЗаверши ее с того места, где ты остановился,"
        "а потом я начну интересоваться твоим настроением и поддерживать тебя 😌"
    )
