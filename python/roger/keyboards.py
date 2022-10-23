from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton 
from sqlite3 import Cursor
from aiogram.utils.callback_data import CallbackData


green_button_answer=InlineKeyboardButton('🟢', callback_data='green_button_answer')
yellow_button_answer=InlineKeyboardButton('🟡', callback_data='yellow_button_answer')
orange_button_answer=InlineKeyboardButton('🟠', callback_data='orange_button_answer')
red_button_answer=InlineKeyboardButton('🔴', callback_data='red_button_answer')
kb_for_mental_poll=InlineKeyboardMarkup(row_width=4).add(green_button_answer, yellow_button_answer, orange_button_answer, red_button_answer)

ask_for_name_yes = InlineKeyboardButton('Это мое имя', callback_data='name_button_yes')
ask_for_name_no = InlineKeyboardButton('Задать другое имя', callback_data='name_button_no')
ask_for_name_kb = InlineKeyboardMarkup().add(ask_for_name_yes, ask_for_name_no)

ask_for_rate_good = InlineKeyboardButton('✅', callback_data='rate_good')
ask_for_rate_bad = InlineKeyboardButton('❌', callback_data='rate_bad')
ask_for_rate_messages = InlineKeyboardMarkup().add(ask_for_rate_good, ask_for_rate_bad)

ask_for_time_to_send_20 = InlineKeyboardButton('20:00-21:00', callback_data='ask_for_time_20')
ask_for_time_to_send_21 = InlineKeyboardButton('21:00-22:00', callback_data='ask_for_time_21')
ask_for_time_to_send_22 = InlineKeyboardButton('22:00-23:00', callback_data='ask_for_time_22')
ask_for_time_to_send_23 = InlineKeyboardButton('23:00-00:00', callback_data='ask_for_time_23')
ask_for_time_to_send_kb = InlineKeyboardMarkup(row_width=2).add(ask_for_time_to_send_20, ask_for_time_to_send_21, ask_for_time_to_send_22, ask_for_time_to_send_23)

