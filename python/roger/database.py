"""DEPRECATED MODULE, REMOVE ALL"""

from bson import ObjectId
from aiogram.types import InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageError

from reg.after_registration import create_new_message_after_registration
from variables import botClient
from keyboards import friend_request_kb
from friends import (
    check_if_user_has_username,
    change_empty_username_to_a_link
)
from db.users import (
    insert_new_user,
    get_user_by_telegram_id
)
from db.friends import (
    insert_new_friends,
    update_friend_status,
    get_friends_record,
)


call_back_approve = CallbackData("Approve", "id", "friend")
call_back_decline = CallbackData("Decline", "id", "friend")


async def create_new_user(
    tg_username: str,
    username: str,
    time_zone: str,
    telegram_id: str,
    user_time: str
):
    """ I DON'T WANT TO WRITE THIS DOC STRING, IT'S 5AM """
    try:
        form_id = ObjectId()
        if tg_username != "":
            tg_username = "@" + tg_username
        else:
            tg_username = " "

        insert_new_user(
            tg_username,
            telegram_id,
            username,
            time_zone,
            user_time
        )

        await botClient.send_message(int(telegram_id), "Отлично! 😍")
        await create_new_message_after_registration(telegram_id, username, form_id)
    except MessageError:
        await botClient.send_message(
            int(telegram_id),
            (
                "Ой, кажется, что-то пошло не так 😞 \n"
                "Повтори действие через несколько минут или "
                "напиши разработчикам через команду /feedback"
            )
        )


async def send_friends_request(tg_id_friend_to: int, friend2: list):
    """ I DON'T WANT TO WRITE THIS DOC STRING, IT'S 5AM """
    try:
        user = get_user_by_telegram_id(tg_id_friend_to)
        insert_new_friends(
            user['_id'],
            friend2['_id'],
            0
        )

        if not check_if_user_has_username(user['telegram_username']):
            user['telegram_username'] = change_empty_username_to_a_link(
                int(user['telegram_id']), user['name'])

        await notify_a_friend_about_friends_request(
            user['telegram_username'],
            user['name'],
            int(friend2['telegram_id']),
            user['telegram_id']
        )
    except MessageError:
        await botClient.send_message(
            int(tg_id_friend_to),
            (
                "Ой, кажется, что-то пошло не так 😞 \n"
                "Повтори действие через несколько минут или "
                "напиши разработчикам через команду /feedback"
            )
        )


async def check_if_user_sent_request(tg_id_friend_from: int, id_friend_to: ObjectId):
    """ I DON'T WANT TO WRITE THIS DOC STRING, IT'S 5AM """
    try:
        user_from = get_user_by_telegram_id(tg_id_friend_from)

        return get_friends_record(user_from['_id'], id_friend_to)
    except MessageError:
        await botClient.send_message(
            tg_id_friend_from,
            (
                "Ой, кажется, что-то пошло не так 😞 \n"
                "Повтори действие через несколько минут или "
                "напиши разработчикам через команду /feedback"
            )
        )


async def check_if_user_got_request(tg_id_friend_to: int, id_friend_from: ObjectId):
    """ I DON'T WANT TO WRITE THIS DOC STRING, IT'S 5AM """
    try:
        user_to = get_user_by_telegram_id(tg_id_friend_to)

        return get_friends_record(id_friend_from, user_to['_id'])
    except MessageError:
        await botClient.send_message(
            tg_id_friend_to,
            (
                "Ой, кажется, что-то пошло не так 😞 \n"
                "Повтори действие через несколько минут или "
                "напиши разработчикам через команду /feedback"
            )
        )


async def notify_a_friend_about_friends_request(
    tg_nickname_friend_from: str,
    tg_name_friend_from: str,
    tg_id_friend_to: int,
    f: str
):
    """ I DON'T WANT TO WRITE THIS DOC STRING, IT'S 5AM """
    friend_request_kb_approve = InlineKeyboardButton(
        '✅', callback_data=call_back_approve.new(id='friend_approve', friend=f))
    friend_request_kb_decline = InlineKeyboardButton(
        '❌', callback_data=call_back_decline.new(id='friend_decline', friend=f))

    friend_request_kb.add(friend_request_kb_approve, friend_request_kb_decline)

    await botClient.send_message(
        int(tg_id_friend_to),
        (
            "Тебе пришел запрос на дружбу от пользователя " + tg_name_friend_from +
            " (" + tg_nickname_friend_from + ")"
        ),
        reply_markup=friend_request_kb
    )


async def is_user_active(id_user: int):
    """ I DON'T WANT TO WRITE THIS DOC STRING, IT'S 5AM """
    try:
        user = get_user_by_telegram_id(str(id_user))

        return user['is_active']
    except MessageError:
        await botClient.send_message(
            int(id_user),
            (
                "Ой, кажется, что-то пошло не так 😞 \n"
                "Повтори действие через несколько минут или "
                "напиши разработчикам через команду /feedback"
            )
        )


async def accept_decline_friend_request(user: int, friend: int, approve: bool):
    """ I DON'T WANT TO WRITE THIS DOC STRING, IT'S 5AM """
    try:
        if approve:
            status = 1
        else:
            status = 2

        user_to = get_user_by_telegram_id(user)
        user_from = get_user_by_telegram_id(friend)

        friends_record = get_friends_record(user_from["_id"], user_to['_id'])
        update_friend_status(friends_record['_id'], status)

        return user_from
    except MessageError:
        await botClient.send_message(
            user,
            (
                "Ой, кажется, что-то пошло не так 😞 \n"
                "Повтори действие через несколько минут или "
                "напиши разработчикам через команду /feedback"
            )
        )
