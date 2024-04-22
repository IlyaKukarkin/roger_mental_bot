"""Module with keyboards and functions to generate keyboards."""

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestUser
)
from aiogram.utils.callback_data import CallbackData

callback_friends_left = CallbackData("L", "id", "index", "len")
callback_friends_right = CallbackData("R", "id", "index", "len")
callback_current_friend_to_delete = CallbackData("D", "id", "friend_id")
callback_friends_support_message = CallbackData("S", "id", "friend_id")
callback_friends_like_support_message = CallbackData(
    "Like", "id", "friend_id", "message_id")

green_button_answer = InlineKeyboardButton(
    '💚', callback_data='green_button_answer')
yellow_button_answer = InlineKeyboardButton(
    '💛', callback_data='yellow_button_answer')
orange_button_answer = InlineKeyboardButton(
    '🧡', callback_data='orange_button_answer')
red_button_answer = InlineKeyboardButton(
    '❤️', callback_data='red_button_answer')
kb_for_mental_poll = InlineKeyboardMarkup(row_width=4).add(
    green_button_answer, yellow_button_answer, orange_button_answer, red_button_answer)

ask_for_name_yes = InlineKeyboardButton(
    'Это мое имя', callback_data='name_button_yes')
ask_for_name_no = InlineKeyboardButton(
    'Задать другое имя', callback_data='name_button_no')
ask_for_name_kb = InlineKeyboardMarkup().add(ask_for_name_yes, ask_for_name_no)

ask_for_rate_good = InlineKeyboardButton('✅', callback_data='rate_good')
ask_for_rate_bad = InlineKeyboardButton('❌', callback_data='rate_bad')
ask_for_rate_messages = InlineKeyboardMarkup().add(
    ask_for_rate_good, ask_for_rate_bad)

ask_for_rate_good_support = InlineKeyboardButton(
    '✅', callback_data='rate_good_support')
ask_for_rate_bad_support = InlineKeyboardButton(
    '❌', callback_data='rate_bad_support')
back_button = InlineKeyboardButton('⬅️ Назад', callback_data='main')

ask_for_rate_messages_support = InlineKeyboardMarkup(row_width=2).add(
    ask_for_rate_good_support, ask_for_rate_bad_support, back_button)


ask_for_time_to_send_20 = InlineKeyboardButton(
    '20:00-21:00', callback_data='ask_for_time_20')
ask_for_time_to_send_21 = InlineKeyboardButton(
    '21:00-22:00', callback_data='ask_for_time_21')
ask_for_time_to_send_22 = InlineKeyboardButton(
    '22:00-23:00', callback_data='ask_for_time_22')
ask_for_time_to_send_23 = InlineKeyboardButton(
    '23:00-00:00', callback_data='ask_for_time_23')
ask_for_time_to_send_kb = InlineKeyboardMarkup(row_width=2).add(
    ask_for_time_to_send_20,
    ask_for_time_to_send_21,
    ask_for_time_to_send_22,
    ask_for_time_to_send_23
)


rate_stata_month = InlineKeyboardButton(
    'За месяц', callback_data='month')
rate_stata_week_2 = InlineKeyboardButton(
    'За 2 недели', callback_data='week2')
rate_stata_week = InlineKeyboardButton(
    'За неделю', callback_data='week')
ask_for_rate_stata_kb = InlineKeyboardMarkup().add(
    rate_stata_month, rate_stata_week_2, rate_stata_week)

feedback_start_button = InlineKeyboardButton(
    'Написать сообщение', callback_data='feedback_start')
feedback_keyboard = InlineKeyboardMarkup().add(
    feedback_start_button)

feedback_finish_button = InlineKeyboardButton(
    '⬅️ Назад', callback_data='feedback_finish')
feedback_finish_keyboard = InlineKeyboardMarkup().add(
    feedback_finish_button)

support_start_button = InlineKeyboardButton(
    'Начать диалог с Роджером', callback_data='support_start')
support_start_keyboard = InlineKeyboardMarkup().add(
    support_start_button)

settings_name = InlineKeyboardButton(
    'Имя', callback_data='settings_name')
settings_timezone = InlineKeyboardButton(
    'Часовой пояс', callback_data='settings_timezone')
settings_time_to_send_messages_button = InlineKeyboardButton(
    'Время отправки сообщений', callback_data='settings_time_to_send_messages_button')
settings_keyboard = InlineKeyboardMarkup(row_width=1).add(
    settings_name, settings_timezone, settings_time_to_send_messages_button)

approve_friends_request = InlineKeyboardButton(
    'Добавить в друзья', callback_data='approve_request')


def create_support_friend_kb(friend_id: str):
    """Returns a keyboard to support a friend (with 1 button "Поддержать")

    Parameters:
    friend_id (str): telegram_id of a friend

    Returns:
    TG InlineKeyboardMarkup
    """

    sendmes_to_friend_button = InlineKeyboardButton(
        'Поддержать', callback_data=callback_friends_support_message.new(
            id='sendmes_to_friend', friend_id=friend_id))

    sendmes_to_friend_kb = InlineKeyboardMarkup(row_width=1).add(
        sendmes_to_friend_button)

    return sendmes_to_friend_kb


def create_friends_keyboard(requests: int, friends: int, add_friends: bool):
    """
    Function to create /friends keyboard

    Parameters:
    requests (int): number of friends requests
    friends (int): number of friends

    Returns:
    TG InlineKeyboardMarkup
    """

    friends_menu_kb = InlineKeyboardMarkup(row_width=1, one_time_keyboard=True)

    if requests > 0:
        friends_requests_button = InlineKeyboardButton(
            '(' + str(requests) + (') Входящие заявки'), callback_data='friends_requests')
        friends_menu_kb = friends_menu_kb.add(friends_requests_button)

    if add_friends:
        add_friends_button = InlineKeyboardButton(
            'Добавить нового друга', callback_data='add_friends')

        friends_menu_kb = friends_menu_kb.add(add_friends_button)

    if friends > 0:
        check_friends_list_button = InlineKeyboardButton(
            'Посмотреть список друзей', callback_data='check_friend_list')
        friends_menu_kb = friends_menu_kb.add(check_friends_list_button)

        delete_friends_list_button = InlineKeyboardButton(
            'Удалить друга', callback_data='delete_friend')
        friends_menu_kb = friends_menu_kb.add(delete_friends_list_button)

    info_friends_button = InlineKeyboardButton(
        'Инфо', callback_data='info_friend_list')

    friends_menu_kb = friends_menu_kb.add(info_friends_button)

    exit_button = InlineKeyboardButton(
        'Выйти', callback_data='main')

    friends_menu_kb = friends_menu_kb.add(exit_button)

    return friends_menu_kb


def create_user_shared_keyboard():
    """
    Function to create user_shared keyboard

    Parameters:

    Returns:
    TG InlineKeyboardMarkup
    """
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True)
    keyboard.add(KeyboardButton("Выбрать контакт",
                 request_user=KeyboardButtonRequestUser(1, user_is_bot=False)))
    keyboard.add(KeyboardButton("⬅️ Назад", callback_data='friends_menu'))
    return keyboard


def create_back_kb(callback_info: str):
    """
    Function to create back keyboard for /friends

    Parameters:
    callback_info (str): callback to return to

    Returns:
    TG InlineKeyboardMarkup
    """

    back_kb = InlineKeyboardMarkup(row_width=1, one_time_keyboard=True)
    return add_back_button(back_kb, callback_info)


def create_exit_kb():
    """
    Function to create exit keyboard

    Parameters:
    callback_info (str): callback to return to

    Returns:
    TG InlineKeyboardMarkup
    """

    exit_kb = InlineKeyboardMarkup(row_width=1, one_time_keyboard=True)
    exit_button = InlineKeyboardButton(
        'Выйти', callback_data="friends_menu")
    exit_kb = exit_kb.add(exit_button)
    return exit_kb


def add_back_button(kb: InlineKeyboardMarkup, callback_info: str):
    """
    Function to add "Back" button for /friends

    Parameters:
    kb (TG InlineKeyboardMarkup): keyboard to add "Back" button
    callback_info (str): callback to return to

    Returns:
    TG InlineKeyboardMarkup
    """

    dymamic_back_button = InlineKeyboardButton(
        '⬅️ Назад', callback_data=callback_info)
    kb = kb.add(dymamic_back_button)

    return kb


def add_delete_from_friends_kb(friends_length: int, index: int,
                               left_index: int, right_index: int, current_friend_id: str):
    """Returns a keyboard to delete friends (for 1 or many)

    Parameters:
    friends_length (int): how many friends user has
    index (int): index of array which indicates what friend is supposed to be shown
    left_index (int): index of array to which user might switch
        (usually index-1, but not necessarily)
    right_index (int): index of array to which user might switch
        (usually index+1, but not necessarily)
    current_friend_id (str): telegram_id of shown friend

    Returns:
    TG InlineKeyboardMarkup (Perfect motherfucking keyboard)
    """
    delete_from_friends_kb = InlineKeyboardMarkup(one_time_keyboard=True)

    delete_from_friends_button = InlineKeyboardButton(
        '❌ Удалить из друзей', callback_data=callback_current_friend_to_delete.new(
            id='friend_to_del', friend_id=current_friend_id))
    delete_from_friends_kb = delete_from_friends_kb.row(
        delete_from_friends_button)

    left_move_button = InlineKeyboardButton(
        f'⬅️ {left_index} из {friends_length}', callback_data=callback_friends_left.new(
            id='go_left', index=index, len=friends_length))
    right_move_button = InlineKeyboardButton(
        f'➡️ {right_index} из {friends_length}', callback_data=callback_friends_right.new(
            id='go_right', index=index, len=friends_length))

    if friends_length == 2 and index == 0:
        delete_from_friends_kb = delete_from_friends_kb.row(right_move_button)

    if friends_length == 2 and index == 1:
        delete_from_friends_kb = delete_from_friends_kb.row(left_move_button)

    if friends_length > 2:
        delete_from_friends_kb = delete_from_friends_kb.row(
            left_move_button, right_move_button)

    exit_button = InlineKeyboardButton(
        'Выйти', callback_data='friends_menu')

    delete_from_friends_kb = delete_from_friends_kb.row(exit_button)

    return delete_from_friends_kb


def create_kb_for_message_like(friend_id: str, message_id: int):
    """Returns a keyboard to like a support message from a friend

    Parameters:
    friend_id (str): telegram_id of a friend

    Returns:
    TG InlineKeyboardMarkup
    """

    like_message_from_friend_button = InlineKeyboardButton(
        '❤️', callback_data=callback_friends_like_support_message.new(
            id='like_mes_from_friend', friend_id=friend_id, message_id=message_id))

    like_message_from_friend_kb = InlineKeyboardMarkup(row_width=1).add(
        like_message_from_friend_button)

    return like_message_from_friend_kb
