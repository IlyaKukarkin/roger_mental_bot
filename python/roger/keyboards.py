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

ask_for_rate_good_support = InlineKeyboardButton('✅', callback_data='rate_good_support')
ask_for_rate_bad_support = InlineKeyboardButton('❌', callback_data='rate_bad_support')
ask_for_rate_messages_support = InlineKeyboardMarkup().add(
    ask_for_rate_good_support, ask_for_rate_bad_support)

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
    'Не отправлять фидбек', callback_data='feedback_finish')
feedback_finish_keyboard = InlineKeyboardMarkup().add(
    feedback_finish_button)

support_start_button = InlineKeyboardButton(
    'Начать диалог с Роджером', callback_data='support_start')
support_start_keyboard = InlineKeyboardMarkup().add(
    support_start_button)

share_contact_button = KeyboardButton('Поделиться контактом друга', request_user=KeyboardButtonRequestUser(123), сallback_data='send_contact')
share_contact_kb = ReplyKeyboardMarkup()
share_contact_kb.add(share_contact_button)

approve_friends_request = InlineKeyboardButton('Добавить в друзья', сallback_data='approve_request')



async def add_button_for_friends_requests(requests: int):
    friends_menu_kb = InlineKeyboardMarkup(row_width=1, one_time_keyboard=True)

    if requests > 0:
         friends_requests_button = InlineKeyboardButton('(' + str(requests) + (') Входящие заявки'), callback_data='friends_internal_requests')
         friends_menu_kb = friends_menu_kb.add(friends_requests_button)

    add_friends_button = InlineKeyboardButton(
    'Добавить нового друга', callback_data='add_friends')

    check_friends_list_button = InlineKeyboardButton(
    'Посмотреть список друзей', callback_data='check_friend_list')

    info_friends_button = InlineKeyboardButton(
    'Инфо', callback_data='info_friend_list')

    friends_menu_kb = friends_menu_kb.add(
    add_friends_button, check_friends_list_button, info_friends_button)

    return friends_menu_kb




