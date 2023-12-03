"""Module providing functions for friends interactions."""

from aiogram.types import (
    ParseMode,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery
)
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.markdown import link

from variables import botClient
from db.friends import (
    get_all_friends,
    get_incoming_requests,
    insert_new_friends,
    get_friends_record,
    update_friend_status
)
from db.users import (
    get_user_by_id,
    get_user_by_telegram_id
)
from common import delete_keyboard
from states import FriendsStates
from keyboards import create_friends_keyboard, create_back_kb


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

    user = get_user_by_telegram_id(str(chat_id))

    friends_requests_count = len(get_incoming_requests(user['_id']))

    friends_count = len(get_all_friends(user['_id']))

    await botClient.send_message(
        chat_id,
        "Выбери действие, которое хочешь выполнить",
        reply_markup=create_friends_keyboard(
            friends_requests_count, friends_count)
    )


async def await_for_a_friend_nickname(callback_query: CallbackQuery):
    """
    NOT USED ANYWHERE!!!
    Callback handler for /friends command

    Parameters:
    callback_query (TG Callback): callback to handle

    Returns:
    None
    """

    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)

    await botClient.send_message(
        callback_query.from_user.id,
        "Введи ник своего друга в Telegram, а я проверю, знаком ли я с ним 🙃"
    )
    await FriendsStates.AwaitForAFriendNicknameToAdd.set()


async def get_friend_nickname(message: Message, state: FSMContext):
    """
    Message handler for /friends command -> Await for a username state

    Parameters:
    message (TG Message): message to handle
    state (TG State): current state

    Returns:
    None
    """

    if message.text == "/stop":
        await state.finish()
        await botClient.send_message(message.chat.id, "Ты вышел из режима ввода")
        return

    if str(message.text)[0] == '/':
        await botClient.send_message(
            message.chat.id,
            (
                "Ты находишься в режиме ввода никнейма друга. "
                "Чтобы выйти из него, выбери команду /stop, "
                "а затем повторно вызови нужную команду"
            )
        )
        await FriendsStates.AwaitForAFriendNicknameToAdd.set()
        return

    if str(message.text)[0] != '@':
        message.text = "@" + message.text

    if message.text == '@':
        await botClient.send_message(
            message.chat.id,
            "Это ник Павла Дурова? Перепроверь и введи корректный ник еще раз 🙃"
        )
        await FriendsStates.AwaitForAFriendNicknameToAdd.set()


async def send_request_to_a_friend(message: Message):
    """
    Message handler for /friends command -> share contact

    Parameters:
    message (TG Message): message to handle

    Returns:
    None
    """

    friend = get_user_by_telegram_id(str(message.user_shared.user_id))

    if friend is None:
        await botClient.send_message(
            message.chat.id,
            (
                "Я не знаю такого пользователя, но буду рад познакомиться! "
                "Отправь своему другу ссылку на @RogerMentalBot и "
                "повтори отправку заявки, когда твой друг зарегистрируется 🙃"
            )
        )
        return

    user_from = get_user_by_telegram_id(str(message.chat.id))

    user_request_sent = get_friends_record(user_from['_id'], friend['_id'])

    if user_request_sent is not None:
        if user_request_sent['status'] == 0:
            await botClient.send_message(
                message.chat.id,
                (
                    "Ты уже отправлял заявку этому пользователю. "
                    "Подожди, пока твой друг примет заявку 🕖"
                )
            )
            return
        if user_request_sent['status'] == 1:
            await botClient.send_message(message.chat.id, "Вы уже дружите 😄")
            return

    user_to = get_user_by_telegram_id(str(message.chat.id))

    user_got_request = get_friends_record(friend['_id'], user_to['_id'])

    if user_got_request is not None:
        if user_got_request['status'] == 0:
            await botClient.send_message(
                message.chat.id,
                (
                    "Тебе этот друг уже отправлял заявку. "
                    "Посмотри, кто уже отправил тебе заявки в друзья: /friends_requests"
                )
            )
            return
        if user_got_request['status'] == 1:
            await botClient.send_message(message.chat.id, "Вы уже дружите 😄")
            return

    user = get_user_by_telegram_id(str(message.chat.id))
    insert_new_friends(
        user['_id'],
        friend['_id'],
        0
    )

    if check_if_user_has_username(user) == False:
        user['telegram_username'] = change_empty_username_to_a_link(
            int(user['telegram_id']), user['name'])
    
    friend_request_kb = InlineKeyboardMarkup()
    friend_request_kb_approve = InlineKeyboardButton(
        '✅', callback_data=call_back_approve.new(id='friend_approve', friend=user['telegram_id']))
    friend_request_kb_decline = InlineKeyboardButton(
        '❌', callback_data=call_back_decline.new(id='friend_decline', friend=user['telegram_id']))

    friend_request_kb.add(friend_request_kb_approve, friend_request_kb_decline)

    await botClient.send_message(
        int(friend['telegram_id']),
        (
            "Тебе пришел запрос на дружбу от пользователя " + user['name'] +
            " \\(" + user['telegram_username'] + "\\)"
        ),
        reply_markup=friend_request_kb, parse_mode=ParseMode.MARKDOWN_V2
    )

    if check_if_user_has_username(friend) == False:
        friend["telegram_username"] = change_empty_username_to_a_link(
            int(friend['telegram_id']), friend['name'])

    await botClient.send_message(
        message.chat.id,
        (
            "Отправил запрос дружбы пользователю " + friend["telegram_username"] +
            "\. Когда твой друг примет запрос в друзья, "
            "ты будешь получать информацию о его настроении"
        ), parse_mode=ParseMode.MARKDOWN_V2
    )


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

        if check_if_user_has_username(friend) == False:
            friend["telegram_username"] = change_empty_username_to_a_link(
                int(friend['telegram_id']), friend['name'])

        friend_list.append(friend)

    usernames = ['😸' + ' ' + friend['telegram_username']
                 for friend in friend_list]
    mes = 'Список друзей, которым доступна информация о твоем настроении:\n\n' + \
        '\n'.join(usernames)

    await botClient.send_message(
        callback_query.from_user.id,
        mes,
        disable_web_page_preview=True,
        reply_markup=create_back_kb("friends_menu"),
    )


async def show_info(callback_query: CallbackQuery):
    """
    Callback handler for /friends command -> "info_friend_list"

    Parameters:
    callback_query (TG Callback): callback to handle

    Returns:
    None
    """

    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)

    mes = """Рассказываю подробнее о режиме «Друзья»

Друзья — это пользователи, которым доступна информация о твоем настроении. Список друзей определяешь только ты.

Как только ты отмечаешь 🔴 или 🟠 настроение, твои друзья получают сообщение об этом —  они смогут написать и поддержать тебя
    """

    await botClient.send_message(callback_query.from_user.id, mes, parse_mode=ParseMode.MARKDOWN)


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
        await botClient.send_message(user_tg_id, "У тебя нет новых заявкок в друзья")
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

        if check_if_user_has_username(friend_user) == False:
            friend_user["telegram_username"] = change_empty_username_to_a_link(
                int(friend_user['telegram_id']), friend_user['name'])

        await botClient.send_message(
            user_tg_id,
            f"Новый запрос в друзья от пользователя {friend_user['telegram_username']}",
            reply_markup=friend_request_kb
        )


async def friends_internal_request(callback_query: CallbackQuery, friend: str, approve: bool):
    """
    Callback handler for /friends command -> "friend_approve" or "friend_approve"

    Parameters:
    callback_query (TG Callback): callback to handle

    Returns:
    None
    """

    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)

    if approve:
        status = 1
    else:
        status = 2

    user_to = get_user_by_telegram_id(str(callback_query.from_user.id))
    user_from = get_user_by_telegram_id(friend)

    friends_record = get_friends_record(user_from["_id"], user_to['_id'])
    friend_obj = update_friend_status(friends_record['_id'], status)

    if check_if_user_has_username(user_from) == False:
        user_from["telegram_username"] = change_empty_username_to_a_link(
            int(user_from['telegram_id']), user_from['name'])

    if approve:
        await botClient.send_message(
            callback_query.from_user.id,
            (
                "Теперь ты дружишь с " + user_from['telegram_username'] + "\. " +
                "Когда твой друг отметит 🔴 или 🟠 настроение, я скажу тебе об этом"
            ), parse_mode=ParseMode.MARKDOWN_V2
        )

        if check_if_user_has_username(user_to) == False:
            user_to["telegram_username"] = change_empty_username_to_a_link(
                int(user_to['telegram_id']), user_to['name'])

        await botClient.send_message(
            user_from["telegram_id"],
            (
                "Теперь ты дружишь с " + user_to['telegram_username'] + "\. " +
                "Когда твой друг отметит 🔴 или 🟠 настроение, я скажу тебе об этом"
            ), parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    await botClient.send_message(
        callback_query.from_user.id,
        f"Ты отклонил заявку в друзья от {user_from['telegram_username']} 🙌"
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

        if check_if_user_has_username(user) == False:
            user["telegram_username"] = change_empty_username_to_a_link(
                int(user['telegram_id']), user['name'])
    try:
        await botClient.send_message(
            friend["telegram_id"],
            (
                "Твой друг " + user['telegram_username'] + " отметил, что сегодня у него " +
                mood_dict[color] +
                " настроение. Ты можешь написать ему напрямую"
            ),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    except: 
        print ("Не удалось отправить сообщение пользователю " + user['telegram_username'])


async def delete_friends(callback_query: CallbackQuery):
    """
    Callback handler for /friends command -> "friend_delete"

    Parameters:
    callback_query (TG Callback): callback to handle

    Returns:
    None
    """

    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await botClient.send_message(
        callback_query.from_user.id,
        'ToDo: доделать удаление друзей'
    )

    # friends_list = await find_all_friends(
    #     await get_user_by_telegram_id(callback_query.from_user.id),
    # )
    # await delete_friends_message(callback_query.from_user.id, friends_list,
    # 0, 0)


# Тут пиздец полный, две неиспользуемые переменные и что вообще происходит в функции
# В конце забыл send_mesasge отправить?? Нет записи в БД о удалении??

# async def delete_friends_message(
#     id_user: int,
#     friends_list: list,
#     index_to_show: int,
#     id_message: int
# ):
#     if len(friends_list) == 0:
#         await botClient.send_message(
#             id_user,
#             "У тебя не осталось друзей 🥲",
#             reply_markup=create_back_kb("friends_menu")
#         )
#         return
#     friends_delete_message_kb = InlineKeyboardMarkup(one_time_keyboard=True)
#     mes = "😻 Твой друг: /n/n"
#     friend = await search_user_by_object_id(friends_list[index_to_show])
#     if check_if_user_has_username(friend['telegram_username']):
#         mes += friend['telegram_username']
#     else:
#         change_empty_username_to_a_link(friend['telegram_id'], friend['name'])
#     friends_button_delete = InlineKeyboardButton(
#         '😿 Удалить друга',
#         callback_data=call_back_decline.new(
#             id='friend_delete',
#             friend_to_delete=friend['_id']
#         )
#     )


# ебануть навигацию везде
