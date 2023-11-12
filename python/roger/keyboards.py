from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButtonRequestUser

green_button_answer = InlineKeyboardButton(
    '🟢', callback_data='green_button_answer')
yellow_button_answer = InlineKeyboardButton(
    '🟡', callback_data='yellow_button_answer')
orange_button_answer = InlineKeyboardButton(
    '🟠', callback_data='orange_button_answer')
red_button_answer = InlineKeyboardButton(
    '🔴', callback_data='red_button_answer')
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


friend_request_kb = InlineKeyboardMarkup()

ask_for_time_to_send_20 = InlineKeyboardButton(
    '20:00-21:00', callback_data='ask_for_time_20')
ask_for_time_to_send_21 = InlineKeyboardButton(
    '21:00-22:00', callback_data='ask_for_time_21')
ask_for_time_to_send_22 = InlineKeyboardButton(
    '22:00-23:00', callback_data='ask_for_time_22')
ask_for_time_to_send_23 = InlineKeyboardButton(
    '23:00-00:00', callback_data='ask_for_time_23')
ask_for_time_to_send_kb = InlineKeyboardMarkup(row_width=2).add(
    ask_for_time_to_send_20, ask_for_time_to_send_21, ask_for_time_to_send_22, ask_for_time_to_send_23)


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


approve_friends_request = InlineKeyboardButton(
    'Добавить в друзья', сallback_data='approve_request')


async def add_button_for_friends_requests(requests: int, friends: int):
    friends_menu_kb = InlineKeyboardMarkup(row_width=1, one_time_keyboard=True)

    if requests > 0:
        friends_requests_button = InlineKeyboardButton(
            '(' + str(requests) + (') Входящие заявки'), callback_data='friends_requests')
        friends_menu_kb = friends_menu_kb.add(friends_requests_button)

    add_friends_button = InlineKeyboardButton(
        'Добавить нового друга', callback_data='add_friends')
    friends_menu_kb = friends_menu_kb.add(add_friends_button)

    if friends > 0:
        check_friends_list_button = InlineKeyboardButton(
            'Посмотреть список друзей', callback_data='check_friend_list')
        friends_menu_kb = friends_menu_kb.add(check_friends_list_button)

        # friends_delete_button = InlineKeyboardButton('Удалить друга', callback_data='delete_from_friends')
        # friends_menu_kb = friends_menu_kb.add(friends_delete_button)

    info_friends_button = InlineKeyboardButton(
        'Инфо', callback_data='info_friend_list')

    back_button = InlineKeyboardButton('⬅️ Назад', callback_data="main")

    friends_menu_kb = friends_menu_kb.add(info_friends_button, back_button)

    return friends_menu_kb


async def create_back_kb(callback_info: str):
    back_kb = InlineKeyboardMarkup(row_width=1, one_time_keyboard=True)
    back_button = InlineKeyboardButton('⬅️ Назад', callback_data=callback_info)
    back_kb = back_kb.add(back_button)
    return back_kb


async def add_back_button(kb: InlineKeyboardMarkup, callback_info: str):
    back_button = InlineKeyboardButton('⬅️ Назад', callback_data=callback_info)
    kb = kb.add(back_button)
    return kb

# ask_for_rate_messages_support = add_back_button(ask_for_rate_messages_support, 'main')

# async def create_delete_friends_kb(callback_info: str):
#     delete_friends_kb = InlineKeyboardMarkup(row_width=1, one_time_keyboard=True)
#     delete_button = InlineKeyboardButton('😿 Удалить из друзей', callback_data=callback_info)
#     delete_friends_kb = delete_friends_kb.add(delete_button)
#     return delete_friends_kb
