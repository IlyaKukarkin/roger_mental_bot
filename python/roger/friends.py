"""Module providing functions for friends interactions."""

from aiogram import dispatcher
from aiogram.types import (
    ParseMode,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery
)
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.markdown import link
from aiogram.utils.exceptions import MessageError


from amplitude_utils import amplitude_send_default_source_event
from variables import botClient, botDispatcher
from db.friends import (
    get_all_friends,
    get_incoming_requests,
    insert_new_friends,
    get_friends_record,
    delete_friends_request,
    add_new_friend,
    delete_from_friends,
    count_all_user_friends_request
)
from db.users import (
    get_user_by_id,
    get_user_by_telegram_id
)
from db.app_settings import App_Settings
from common import delete_keyboard
from states import Recording
from keyboards import (
    create_friends_keyboard,
    create_back_kb,
    add_delete_from_friends_kb,
    create_support_friend_kb,
    create_exit_kb
)


call_back_approve = CallbackData("Approve", "id", "friend")
call_back_decline = CallbackData("Decline", "id", "friend")
call_back_delete = CallbackData("Delete", "id", "friend_to_delete")


def check_if_user_has_username(user: dict):
    """Check if username exists and validate username"""
    if user['telegram_username'] in ('@', ' ', ''):
        return False
    return True


def change_empty_username_to_a_link(user_id: int, name: str):
    """ Change empty username to a link """
    return link(name, f"tg://user?id={user_id}")


async def get_menu_for_command(chat_id: int):
    """
    Message handler for /friends command

    Parameters:
    chat_id (int): user Telegram ID

    Returns:
    None
    """
    app_settings = App_Settings()
    settings = app_settings.get_app_settings()

    user = get_user_by_telegram_id(str(chat_id))

    friends_requests_count = len(get_incoming_requests(user['_id']))

    friends_count = len(get_all_friends(user['_id']))

    if friends_count < settings['friends_limit']:
        await botClient.send_message(
            chat_id,
            "Выбери действие, которое хочешь выполнить",
            reply_markup=create_friends_keyboard(
                friends_requests_count, friends_count, friends_count < settings['friends_limit'])
        )

    else:
        await botClient.send_message(
            chat_id,
            "Выбери действие, которое хочешь выполнить\\.\n\n"
            "Обрати внимание\\: ты достиг лимита по числу друзей\\. "
            f"Текущий лимит: {settings['friends_limit']} друга\\.",
            reply_markup=create_friends_keyboard(
                friends_requests_count, friends_count, friends_count < settings['friends_limit']),
            parse_mode=ParseMode.MARKDOWN_V2
        )

# Починить: очень много if-ов, нужне переформатировать
# pylint: disable=too-many-branches


async def send_request_to_a_friend(message: Message):
    """
    Message handler for /friends command -> share contact

    Parameters:
    message (TG Message): message to handle

    Returns:
    None
    """
    try:

        friend = get_user_by_telegram_id(str(message.user_shared.user_id))

        reply_message = ''

        if friend is None:
            reply_message = (
                "Я не знаю такого пользователя, но буду рад познакомиться\\!\n\n"
                "Отправь своему другу ссылку на меня "
                "https://t\\.me/rogermentalbot\\?start\\=friends и "
                "повтори отправку заявки, когда твой друг зарегистрируется 🙃"
            )

        app_settings = App_Settings()
        settings = app_settings.get_app_settings()

        user_from = get_user_by_telegram_id(str(message.chat.id))

        if not reply_message and count_all_user_friends_request(
                user_from) + len(user_from["friends"]) >= settings['friends_limit']:
            reply_message = (
                f"""Ты превысил лимит на число друзей и заявок в друзья 🥲

                Вот что ты можешь сделать:
                1. Проверь входящие заявки в друзья по команде /friends_requests
                2. Подожди, пока друзья примут отправленные тобой заявки
                3. Удали друзей, если считаешь нужным

Всего ты можешь иметь не более {settings['friends_limit']} друзей и активных заявок в друзья"""
            )

        if not reply_message and len(
                friend["friends"]) >= settings['friends_limit']:
            reply_message = (
                f"""Твой друг уже добавил себе {settings['friends_limit']} друга 🥲

                Ты сможешь подружиться с ним, если он удалит кого-нибудь из своих друзей"""
            )

        if not reply_message and len(friend["friends"]) + \
                count_all_user_friends_request(friend) >= settings['friends_limit']:
            reply_message = (
                "Твой друг уже израсходовал свой лимит на число друзей"
                "и активных заявок в друзья 🥲"
            )

        if not reply_message and not friend["is_active"]:
            reply_message = (
                "Я знаю этого пользователя, но он перестал замерять настроение со мной 🥲\n\n"
                "Попроси его перейти по ссылке https://t\\.me/rogermentalbot\\?start\\=friends "
                "и зарегистрироваться в Роджере, чтобы ты смог подружиться с ним"
            )

        if not reply_message and user_from["_id"] == friend["_id"]:
            reply_message = (
                "Себя пока нельзя добавлять в друзья 😁"
            )

        if not reply_message and "friends" in user_from:
            for f in user_from["friends"]:
                if f == friend["_id"]:
                    reply_message = (
                        "Вы уже дружите 😸"
                    )

        user_request_sent = get_friends_record(user_from['_id'], friend['_id'])

        if not reply_message and user_request_sent is not None:
            reply_message = (
                "Ты уже отправлял заявку этому пользователю. "
                "Подожди, пока твой друг примет заявку 🕖"
            )

        user_got_request = get_friends_record(friend['_id'], user_from['_id'])

        if not reply_message and user_got_request is not None:
            reply_message = (
                "Этот друг уже отправил тебе заявку. "
                "Посмотри, кто уже отправил тебе заявки в друзья: /friends_requests"
            )

        if reply_message:
            await botClient.send_message(
                message.chat.id,
                reply_message,
                reply_markup=create_back_kb("friends_menu")
            )
            return

        if not check_if_user_has_username(user_from):
            user_from['telegram_username'] = change_empty_username_to_a_link(
                int(user_from['telegram_id']), user_from['name'])

        friend_request_kb = InlineKeyboardMarkup()
        friend_request_kb_approve = InlineKeyboardButton(
            '✅', callback_data=call_back_approve.new(id='friend_approve',
                                                     friend=user_from['telegram_id']))
        friend_request_kb_decline = InlineKeyboardButton(
            '❌', callback_data=call_back_decline.new(id='friend_decline',
                                                     friend=user_from['telegram_id']))

        friend_request_kb.add(
            friend_request_kb_approve,
            friend_request_kb_decline)

        mes = "Тебе пришел запрос на дружбу от пользователя " + \
            user_from['telegram_username'] + "\\.\n\n" + \
            "Если ты примешь этот запрос, твой друг начнет получать уведомления," + \
            " когда ты отметишь 🔴 или 🟠 настроение"
        mes = mes.replace("@", "\\@")
        mes = mes.replace("_", "\\_")

        await botClient.send_message(
            int(friend['telegram_id']),
            mes,
            reply_markup=friend_request_kb, parse_mode=ParseMode.MARKDOWN_V2
        )

        insert_new_friends(
            user_from['_id'],
            friend['_id']
        )

        if not check_if_user_has_username(friend):
            friend["telegram_username"] = change_empty_username_to_a_link(
                int(friend['telegram_id']), friend['name'])

        mes = "Отправил запрос дружбы пользователю " + friend["telegram_username"] + \
            "\\. Когда твой друг примет запрос в друзья, " + \
            "ты начнешь получать информацию о его 🔴 или 🟠 настроении"
        mes = mes.replace("@", "\\@")
        mes = mes.replace("_", "\\_")

        await botClient.send_message(
            message.chat.id,
            mes,
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True,
            reply_markup=create_back_kb("friends_menu")
        )

    # Починить: отлавливать ошибку по блокировке бота, прежде чем ловить общую ошибку
    # pylint: disable=broad-exception-caught
    except Exception as e:
        # на случай, если friend в процессе оформления заявки задизейблил бота
        await amplitude_send_default_source_event("Error",
                                                  str(message.chat.id),
                                                  "Friends. Exception While Adding Friend",
                                                  e)
        await botClient.send_message(
            message.chat.id,
            (
                "Я не знаю такого пользователя, но буду рад познакомиться\\!\n\n"
                "Отправь своему другу ссылку на Роджера "
                "https://t\\.me/rogermentalbot\\?start\\=friends и "
                "повтори отправку заявки, когда твой друг зарегистрируется 🙃"
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True,
            reply_markup=create_back_kb("friends_menu")
        )
        return


async def show_active_friends(callback_query: CallbackQuery):
    """
    Callback handler for /friends command -> "check_friend_list"

    Parameters:
    callback_query (TG Callback): callback to handle

    Returns:
    None
    """

    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)

    user = get_user_by_telegram_id(str(callback_query.from_user.id))

    friends_id_list = get_all_friends(user['_id'])

    if len(friends_id_list) == 0:
        await botClient.send_message(
            callback_query.from_user.id,
            (
                "У тебя пока нет друзей. Чтобы добавить первого друга, "
                "введи команду /friends и нажми кнопку Добавить нового друга"
            )
        )
        return

    friend_list = []

    for friend_id in friends_id_list:

        friend = get_user_by_id(friend_id)

        if not check_if_user_has_username(friend):
            friend["telegram_username"] = change_empty_username_to_a_link(
                int(friend['telegram_id']), friend['name'])

        friend_list.append(friend['telegram_username'])

    usernames = ['😸 ' + friend
                 for friend in friend_list]

    mes = 'Список друзей, которым доступна информация о твоем настроении:\n\n' + \
        '\n'.join(usernames)

    mes = mes.replace("@", "\\@")
    mes = mes.replace("_", "\\_")

    await botClient.send_message(
        callback_query.from_user.id,
        mes,
        disable_web_page_preview=True,
        reply_markup=create_back_kb("friends_menu"),
        parse_mode=ParseMode.MARKDOWN_V2
    )


async def show_info(callback_query: CallbackQuery):
    """
    Callback handler for /friends command -> "info_friend_list"

    Parameters:
    callback_query (TG Callback): callback to handle

    Returns:
    None
    """

    app_settings = App_Settings()
    settings = app_settings.get_app_settings()

    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)

    mes = f"""Рассказываю подробнее о режиме «Друзья».

Друзья — это пользователи, которым доступна информация о твоем настроении. Список друзей определяешь только ты.

Как только ты отмечаешь 🔴 или 🟠 настроение, твои друзья получают сообщение об этом — они смогут написать и поддержать тебя.

Обрати внимание: всего ты можешь добавить не более {settings['friends_limit']} друзей. Добавляй только самых близких!
    """

    await botClient.send_message(callback_query.from_user.id,
                                 mes,
                                 parse_mode=ParseMode.MARKDOWN,
                                 reply_markup=create_back_kb("friends_menu"))


async def watch_friends_internal_requests(
    user_tg_id: int,
    message_id: int,
    keyboard_delete_need: bool
):
    """
    Callback handler for /friends command -> "friends_requests"

    Parameters:
    callback_query (TG Callback): callback to handle

    Returns:
    None
    """

    if keyboard_delete_need:
        await delete_keyboard(user_tg_id, message_id)

    user = get_user_by_telegram_id(str(user_tg_id))

    incoming_requests = get_incoming_requests(user['_id'])

    if len(incoming_requests) == 0:
        await botClient.send_message(user_tg_id, "У тебя нет новых заявок в друзья")
        return

    for request_user_id in incoming_requests:
        friend_request_kb = InlineKeyboardMarkup()

        friend_user = get_user_by_id(request_user_id)
        friend_telegram_id = friend_user["telegram_id"]

        friend_request_kb_approve = InlineKeyboardButton(
            '✅',
            callback_data=call_back_approve.new(
                id='friend_approve', friend=friend_telegram_id)
        )
        friend_request_kb_decline = InlineKeyboardButton(
            '❌',
            callback_data=call_back_decline.new(
                id='friend_decline', friend=friend_telegram_id)
        )

        friend_request_kb.add(friend_request_kb_approve,
                              friend_request_kb_decline)

        if not check_if_user_has_username(friend_user):
            friend_user["telegram_username"] = change_empty_username_to_a_link(
                int(friend_user['telegram_id']), friend_user['name'])

        mes = f"Новый запрос в друзья от пользователя {friend_user['telegram_username']}\\.\n\n" + \
            "Если ты примешь этот запрос, твой друг начнет " + \
            "получать уведомления, когда ты отметишь 🔴 или 🟠 настроение"

        mes = mes.replace("@", "\\@")
        mes = mes.replace("_", "\\_")

        await botClient.send_message(
            user_tg_id,
            mes,
            reply_markup=friend_request_kb,
            parse_mode=ParseMode.MARKDOWN_V2
        )


async def friends_internal_request(callback_query: CallbackQuery, friend: str, approve: bool):
    """
    Callback handler for /friends command -> "friend_approve" or "friend_approve" or decline

    Parameters:
    callback_query (TG Callback): callback to handle

    Returns:
    None
    """

    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)

    user_to = get_user_by_telegram_id(str(callback_query.from_user.id))
    user_from = get_user_by_telegram_id(friend)

    if not check_if_user_has_username(user_from):
        user_from["telegram_username"] = change_empty_username_to_a_link(
            int(user_from['telegram_id']), user_from['name'])

    delete_friends_request(user_to["_id"], user_from["_id"])

    if approve:

        add_new_friend(user_to["_id"], user_from["_id"])

        mes = "Теперь ты дружишь с " + user_from['telegram_username'] + "\\. " + \
              "Когда твой друг отметит 🔴 или 🟠 настроение, я скажу тебе об этом"

        mes = mes.replace("@", "\\@")
        mes = mes.replace("_", "\\_")

        await botClient.send_message(
            callback_query.from_user.id,
            mes,
            parse_mode=ParseMode.MARKDOWN_V2
        )

        if not check_if_user_has_username(user_to):
            user_to["telegram_username"] = change_empty_username_to_a_link(
                int(user_to['telegram_id']), user_to['name'])

        mes = "Теперь ты дружишь с " + user_to['telegram_username'] + "\\. " + \
              "Когда твой друг отметит 🔴 или 🟠 настроение, я скажу тебе об этом"

        mes = mes.replace("@", "\\@")
        mes = mes.replace("_", "\\_")

        await botClient.send_message(
            user_from["telegram_id"],
            mes,
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    mes = "Ты отклонил заявку в друзья от " + \
        user_from['telegram_username'] + " 🙌"

    mes = mes.replace("@", "\\@")
    mes = mes.replace("_", "\\_")

    await botClient.send_message(
        callback_query.from_user.id,
        mes,
        parse_mode=ParseMode.MARKDOWN_V2
    )


async def send_a_friend_message_about_bad_mood(tg_id_user: int, color: str):
    """
    Function to send message to user friends

    Parameters:
    tg_id_user (int): Telegrame ID of user to send message to his friends
    color (str): can be "red" or "orange"

    Returns:
    None
    """

    mood_dict = {'green': "🟢", 'yellow': "🟡", 'orange': "🟠", 'red': "🔴"}
    user = get_user_by_telegram_id(str(tg_id_user))
    friends = get_all_friends(user['_id'])

    if len(friends) == 0:
        return

    for friend_user_id in friends:
        friend = get_user_by_id(friend_user_id)

        if not check_if_user_has_username(user):
            user["telegram_username"] = change_empty_username_to_a_link(
                int(user['telegram_id']), user['name'])
        try:
            print(2)
            mes = "Твой друг " + user['telegram_username'] + \
                  " отметил, что сегодня у него " + \
                mood_dict[color] + \
                  " настроение\\. Ты можешь написать ему по кнопке ниже"

            mes = mes.replace("@", "\\@")
            mes = mes.replace("_", "\\_")
            print(mes)
            await botClient.send_message(
                int(friend["telegram_id"]),
                mes,
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True,
                reply_markup=create_support_friend_kb(str(tg_id_user))
            )
        except MessageError:
            print(
                "Не удалось отправить сообщение пользователю " +
                user['telegram_username'])
        # pylint: disable=broad-exception-caught
        except Exception as e:
            print(e)
            await amplitude_send_default_source_event("Error",
                                                      friend["telegram_id"],
                                                      "send_a_friend_message_about_bad_mood",
                                                      e)


async def delete_from_friends_message(callback_query: CallbackQuery, index: int):
    "main function to delete friends"

    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)

    user = get_user_by_telegram_id(str(callback_query.from_user.id))

    friends = get_all_friends(user['_id'])

    current_friend = get_user_by_id(friends[index])

    if not check_if_user_has_username(current_friend):
        current_friend['telegram_username'] = change_empty_username_to_a_link(
            int(current_friend['telegram_id']), current_friend['name'])

    left_index, right_index = calculating_indexes_for_delete_kb_friends(
        index, len(friends))

    mes = f"""*Друг {index+1} из {len(friends)}*\n
Удалить пользователя {current_friend['telegram_username']} из друзей\\?\n
Если ты удалишь друга, он больше не сможет получать информацию о твоем настроении"""
    mes = mes.replace("@", "\\@")
    mes = mes.replace("_", "\\_")

    await botClient.send_message(
        callback_query.from_user.id,
        mes,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=add_delete_from_friends_kb(
            len(friends), index, left_index, right_index, str(
                current_friend["telegram_id"]))
    )


def calculating_indexes_for_delete_kb_friends(index: int, len_array: int):
    "индексы чисто для фронта, для обращения через них к массиву сделай -1"
    index += 1

    left_index = index - 1
    right_index = index + 1

    if left_index < 1:
        left_index = len_array

    if right_index > len_array:
        right_index = 1

    return left_index, right_index


async def delete_from_friends_go(callback_query: CallbackQuery,
                                 index: int,
                                 number_of_friends: int,
                                 direction: str):
    """allows user to choose which friend should be deleted"""

    if direction == "left":
        index = index - 1

    if direction == "right":
        index = index + 1

    if index < 0:
        index = number_of_friends - 1

    if index == number_of_friends:
        index = 0

    await delete_from_friends_message(callback_query, index)


async def delete_friend(callback_query: CallbackQuery, friend_id: str):
    """finishes delete a friend"""

    user = get_user_by_telegram_id(str(callback_query.from_user.id))

    current_friend = get_user_by_telegram_id(friend_id)

    delete_from_friends(user["_id"], current_friend["_id"])

    if not check_if_user_has_username(current_friend):
        current_friend['telegram_username'] = change_empty_username_to_a_link(
            int(current_friend['telegram_id']), current_friend['name'])

    mes = f"Удалил пользователя {current_friend['telegram_username']} из твоих друзей 🙌"
    mes = mes.replace("@", "\\@")
    mes = mes.replace("_", "\\_")

    if (len(user["friends"])) == 1:
        # 1, потому что не обновляем переменную после удаления
        await botClient.send_message(
            callback_query.from_user.id,
            mes,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=create_exit_kb()
        )
        return

    await botClient.send_message(
        callback_query.from_user.id,
        mes,
        parse_mode=ParseMode.MARKDOWN_V2
    )

    await delete_from_friends_message(callback_query, 0)


async def support_friend(callback_query: CallbackQuery, friend_id: str):
    """
    start to create a support mes for friend
    """
    await botClient.send_message(
        callback_query.from_user.id,
        ("""Напиши сообщение ниже, а я передам его твоему другу.

Не отправляй медиафайлы, я умею передавать только текстовые сообщения"""),
        reply_markup=create_back_kb("main")
    )
    await Recording.AwaitForASupportMessageFromFriend.set()
    state = botDispatcher.get_current().current_state()
    await state.update_data(friend_id=friend_id)


async def sendmes_to_support_friend(friend_id: str, message: Message, state: dispatcher.FSMContext):
    """
    function sends a message to a user's friend
    """
    user = get_user_by_telegram_id(str(message.chat.id))

    if not check_if_user_has_username(user):
        user['telegram_username'] = change_empty_username_to_a_link(
            int(user['telegram_id']), user['name'])

    mes = f"""Твой друг {user['telegram_username']} поддерживает тебя\\.

Вот его сообщение\\: """
    mes = mes.replace("@", "\\@")
    mes = mes.replace("_", "\\_")

    await botClient.send_message(
        int(friend_id),
        mes,
        parse_mode=ParseMode.MARKDOWN_V2
    )

    await botClient.send_message(
        int(friend_id), message.text)

    await botClient.send_message(
        int(user["telegram_id"]), "Твое сообщение доставлено другу 💙")

    await state.finish()
