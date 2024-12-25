"""Main module with all BOT handlers."""
# pylint: disable=global-statement

import os
import json
from datetime import datetime
from bson import ObjectId
from aiogram.utils import executor
from aiogram import types, dispatcher
from aiogram.utils.callback_data import CallbackData
from amplitude import Amplitude
from logger import logger

from db.setup import dbClient
from db.users import (
    update_user_is_active,
    get_user_by_telegram_id
)
from singleton import SingletonClass
from states import Recording, Registration
from common import delete_keyboard
from feedback import feedback_start, feedback_get_text_from_user, feedback_get_photo_from_user
from version import version_command
from restart import restart_command
from sendmestoall import send_message_to_all, get_message_to_all
from start import start_command
from reg.reg_user_name import get_user_name, get_printed_user_name, get_customer_name
from reg.reg_user_time import (
    get_user_time_to_send_messages,
    user_time_20,
    user_time_21,
    user_time_22,
    user_time_23
)
from reg.reg_user_timezone import get_user_timezone, customer_timezone
from reg.after_registration import create_new_message_after_registration
from stata import stata_show_mes, delete_from_cart_handler1
from ratestata import send_rate_stata, get_rate_stata
from sendmessage import sendmes, callback_after_click_on_color_button
from sendnewyearmessage import send_new_year_message
from variables import botClient, botDispatcher
from handlers import rate_message
from fillform import fillform_command
from feedback_answer import feedback_answer_start, feedback_send_text_to_user
from settings import settings_main, check_to_send_mes
from amplitude_utils import amplitude_send_default_source_event
from chatgpt import (
    support_message,
    await_for_a_problem,
    callback_after_click_on_button_support,
    support_callback
)
from friends import (
    get_menu_for_command,
    show_active_friends,
    show_info,
    watch_friends_internal_requests,
    send_request_to_a_friend,
    friends_internal_request,
    delete_from_friends_message,
    delete_from_friends_go,
    delete_friend,
    support_friend,
    sendmes_to_support_friend,
    like_on_support_friend,
    call_back_approve,
    call_back_decline
)
from keyboards import (
    create_user_shared_keyboard,
    callback_friends_left,
    callback_friends_right,
    callback_current_friend_to_delete,
    callback_friends_support_message,
    callback_friends_like_support_message
)

singleton = SingletonClass()
singleton.collection_name = dbClient

# текущая версия бота
VERSION = "2.5.3"

# read texts from json file
with open('texts.json', encoding="utf-8") as t:
    texts = json.load(t)

# Init Amplitude
amplitude_api_key = os.getenv("AMPLITUDE_API_KEY")
amplitude = Amplitude(amplitude_api_key)


@botDispatcher.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    """команда старт при первом запуске бота"""
    args = message.get_args()
    if args is None:
        args = ""
    await start_command(message, args)


@botDispatcher.message_handler(commands=['version'])
async def process_version_command(message: types.Message):
    """версия бота"""
    await version_command(message, VERSION)


@botDispatcher.message_handler(commands=['restart'])
async def process_restart_command(message: types.Message):
    """Перезагрузка ботов"""
    await restart_command(message)


@botDispatcher.message_handler(commands=['friends'])
async def friends_command(message: types.Message):
    """друзья"""
    await amplitude_send_default_source_event("Friends. Command Called",
                                              str(message.chat.id),
                                              "",
                                              "")
    await get_menu_for_command(message.chat.id)


@botDispatcher.callback_query_handler(lambda c: c.data == 'main', state='*')
async def any_state_main_handler(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    """дефолтный хандлер любого стейта"""
    await amplitude_send_default_source_event("Back Button. Pressed",
                                              str(callback_query.from_user.id),
                                              "",
                                              "")
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await state.finish()
    await botClient.answer_callback_query(
        callback_query.id,
        'Ты вышел из прошлого режима, можешь выбрать другой 😌'
    )


@botDispatcher.callback_query_handler(lambda c: c.data == 'friends_menu')
async def show_menu(callback_query: types.CallbackQuery):
    """показать меню друзей"""
    await amplitude_send_default_source_event("Friends. Menu Called",
                                              str(callback_query.from_user.id),
                                              "",
                                              "")
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await get_menu_for_command(callback_query.from_user.id)


@botDispatcher.callback_query_handler(lambda c: c.data == 'add_friends')
async def add_friends_handler(callback_query: types.CallbackQuery):
    """хандлер добавить друзей"""
    await amplitude_send_default_source_event("Friends. Add Friends. Command Called",
                                              str(callback_query.from_user.id),
                                              "",
                                              "")
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)

    await botClient.send_message(
        callback_query.from_user.id,
        "Выбери контакт в Telegram, который хочешь добавить в друзья",
        reply_markup=create_user_shared_keyboard()
    )
    await Recording.AwaitForAFriendContact.set()


@botDispatcher.message_handler(content_types=types.ContentType.USER_SHARED,
                               state=Recording.AwaitForAFriendContact)
async def contacts(msg: types.Message, state: dispatcher.FSMContext):
    """хандлер для шеринга контакта друга"""
    await amplitude_send_default_source_event("Friends Sharing Contact",
                                              str(msg.chat.id),
                                              str(msg.user_shared.user_id),
                                              "")
    await msg.answer(
        "Вычисляю, знаком ли я с твоим другом...",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await send_request_to_a_friend(msg)
    await state.finish()


@botDispatcher.message_handler(lambda message: message.text == '⬅️ Назад',
                               state=Recording.AwaitForAFriendContact)
async def back_from_sharing_friends(msg: types.Message, state: dispatcher.FSMContext):
    """выход из режима шеринга контакта друга"""
    await amplitude_send_default_source_event("Friends. Sharing Contact. Back Button",
                                              str(msg.chat.id),
                                              "",
                                              "")
    await get_menu_for_command(msg.chat.id)
    await state.finish()


@botDispatcher.callback_query_handler(
    call_back_approve.filter(id='friend_approve'))
async def process_callback_friend_request_approve_button(
    callback_query: types.CallbackQuery,
    callback_data: dict
):
    """аппрув друга"""
    await amplitude_send_default_source_event("Friends Request. Button Pressed",
                                              str(callback_query.from_user.id),
                                              "Approve",
                                              "")
    friend = callback_data.get("friend")
    await friends_internal_request(callback_query, friend, True)


@botDispatcher.callback_query_handler(
    call_back_decline.filter(id='friend_decline'))
async def process_callback_friend_request_decline_button(
    callback_query: types.CallbackQuery,
    callback_data: dict
):
    """отказ от друга"""
    await amplitude_send_default_source_event("Friends Request. Button Pressed",
                                              str(callback_query.from_user.id),
                                              "Decline",
                                              "")
    friend = callback_data.get("friend")
    await friends_internal_request(callback_query, friend, False)


@botDispatcher.callback_query_handler(lambda c: c.data == 'check_friend_list')
async def friends_list_handler(callback_query: types.CallbackQuery):
    """вывод списка активных друзей"""
    await amplitude_send_default_source_event("Active Friends List. Command Called",
                                              str(callback_query.from_user.id),
                                              "",
                                              "")
    await show_active_friends(callback_query)


@botDispatcher.callback_query_handler(lambda c: c.data == 'info_friend_list')
async def friends_info_handler(callback_query: types.CallbackQuery):
    """вывод информации о режиме друзья"""
    await amplitude_send_default_source_event("Friends Info. Command Called",
                                              str(callback_query.from_user.id),
                                              "",
                                              "")
    await show_info(callback_query)


@botDispatcher.callback_query_handler(lambda c: c.data == 'delete_friend')
async def friends_delete_handler(callback_query: types.CallbackQuery):
    """удалить из друзей"""
    await amplitude_send_default_source_event("Friends. Delete Command Called",
                                              str(callback_query.from_user.id),
                                              "",
                                              "")
    await delete_from_friends_message(callback_query, 0)


@botDispatcher.callback_query_handler(
    callback_friends_left.filter(id='go_left'))
async def delete_from_friends_go_left_callback(callback_query: types.CallbackQuery,
                                               callback_data: dict):
    """удаление из друзей go left"""
    index = callback_data.get("index")
    number_of_friends = callback_data.get("len")
    await amplitude_send_default_source_event("Friends. Delete. Go left called",
                                              str(callback_query.from_user.id),
                                              "",
                                              "")
    await delete_from_friends_go(callback_query, int(index), int(number_of_friends), 'left')


@botDispatcher.callback_query_handler(
    callback_friends_right.filter(id='go_right'))
async def delete_from_friends_go_right_callback(callback_query: types.CallbackQuery,
                                                callback_data: dict):
    """удаление из друзей go right"""
    index = callback_data.get("index")
    number_of_friends = callback_data.get("len")
    await amplitude_send_default_source_event("Friends. Delete. Go right called",
                                              str(callback_query.from_user.id),
                                              "",
                                              "")
    await delete_from_friends_go(callback_query, int(index), int(number_of_friends), 'right')


@botDispatcher.callback_query_handler(
    callback_current_friend_to_delete.filter(id='friend_to_del'))
async def delete_from_friends_callback(callback_query: types.CallbackQuery,
                                       callback_data: dict):
    """удаление друга"""
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    friend_id = callback_data.get("friend_id")
    await amplitude_send_default_source_event("Friends. Delete. Delete Button Pressed",
                                              str(callback_query.from_user.id),
                                              str(friend_id),
                                              "")
    await delete_friend(callback_query, friend_id)


@botDispatcher.callback_query_handler(lambda c: c.data == 'friends_requests')
async def friends_request_handler(callback_query: types.CallbackQuery):
    """добавить друга"""
    await amplitude_send_default_source_event("Friends Requests. Button Pressed",
                                              str(callback_query.from_user.id),
                                              "",
                                              "")
    await watch_friends_internal_requests(
        callback_query.from_user.id,
        callback_query.message.message_id,
        True
    )


@botDispatcher.callback_query_handler(
    callback_friends_support_message.filter(id='sendmes_to_friend'))
async def sendmes_to_friend_callback(callback_query: types.CallbackQuery,
                                     callback_data: dict):
    """отправка сообщения другу со словами поддержки"""
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    friend_id = callback_data.get("friend_id")
    await amplitude_send_default_source_event("Friends. Support Button Pressed",
                                              str(callback_query.from_user.id),
                                              "",
                                              "")
    await support_friend(callback_query, friend_id)


@botDispatcher.callback_query_handler(
    callback_friends_like_support_message.filter(id='like_mes_from_friend'))
async def like_mes_from_friend_callback(callback_query: types.CallbackQuery,
                                        callback_data: dict):
    """лайк на сообщение со словами поддержки от друга"""
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    friend_id = callback_data.get("friend_id")
    message_id = callback_data.get("message_id")
    await amplitude_send_default_source_event("Friends. Like on Button with Support Pressed",
                                              str(callback_query.from_user.id),
                                              "",
                                              "")
    await botClient.answer_callback_query(
        callback_query.id,
        'Отправил другу твой лайк ❤️'
    )
    await like_on_support_friend(callback_query, friend_id, message_id)


@botDispatcher.message_handler(
    state=Recording.AwaitForASupportMessageFromFriend)
async def sendmes_support_to_a_friend(
    message: types.Message,
    state: dispatcher.FSMContext
):
    """отправка сообщения другу со словами поддержки"""
    data = await state.get_data()
    await delete_keyboard(message.chat.id, data["message_with_button_id"])
    await amplitude_send_default_source_event("Friends. Support to a Friend Sent",
                                              str(message.chat.id),
                                              data["friend_id"],
                                              message.text)
    await sendmes_to_support_friend(data["friend_id"], message, state)


@botDispatcher.message_handler(commands=['friends_requests'])
async def friends_request_command(message: types.Message):
    """запросы на добавление друзей"""
    await amplitude_send_default_source_event("Friends Requests. Command Called",
                                              str(message.chat.id),
                                              "",
                                              "")
    await watch_friends_internal_requests(message.chat.id, message.message_id, False)

# вывод статистики по созданному пользователем сообщению
# колбек для обработки статистики по сообщению пользователя
cart_cb = CallbackData("q", "id", "button_parameter")


@botDispatcher.message_handler(commands=['stata'])
async def process_stata_command(message: types.Message):
    """вывод статистики по сообщению поддержки"""
    await amplitude_send_default_source_event("Stata. Command Called",
                                              str(message.chat.id),
                                              "",
                                              "")
    await botClient.send_message(message.chat.id, "Произвожу вычисления, немного терпения 😌")
    await stata_show_mes(message)


@botDispatcher.callback_query_handler(
    cart_cb.filter(button_parameter=["kb_mes"]))
async def delete_from_cart_handler(call: types.CallbackQuery, callback_data: dict):
    """коллбек с сообщением для запроса статистики"""
    await botClient.send_message(call.from_user.id, "Подгружаю статистику, немного терпения 😌")
    await delete_from_cart_handler1(call, callback_data)


@botDispatcher.message_handler(commands=['mentalstata'])
async def process_rate_stata_command(message: types.Message):
    """вывод статистики по замерам настроения"""
    await amplitude_send_default_source_event("MentalStata. Command Called",
                                              str(message.chat.id),
                                              "",
                                              "")
    await get_rate_stata(message)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'month')
async def rate_stata_handler_month(
    callback_query: types.CallbackQuery
):
    """вывод статистики настроения за месяц"""
    await amplitude_send_default_source_event("MentalStata. Button Month Pressed",
                                              str(callback_query.from_user.id),
                                              "Month",
                                              "")
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await send_rate_stata(callback_query.from_user.id, 'month')


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'week2')
async def rate_stata_handler_week2(
    callback_query: types.CallbackQuery
):
    """вывод статистики настроения за две недели"""
    await amplitude_send_default_source_event("MentalStata. Button TwoWeeks Pressed",
                                              str(callback_query.from_user.id),
                                              "Two Weeks",
                                              "")
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await send_rate_stata(callback_query.from_user.id, 'week2')


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'week')
async def rate_stata_handler_week(
    callback_query: types.CallbackQuery
):
    """вывод статистики настроения за неделю"""
    await amplitude_send_default_source_event("MentalStata. Button Week Pressed",
                                              str(callback_query.from_user.id),
                                              "Week",
                                              "")
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await send_rate_stata(callback_query.from_user.id, 'week')


@botDispatcher.message_handler(commands=['fillform'])
async def process_fillform_command(message: types.Message):
    """заполняем форму по команде"""
    await amplitude_send_default_source_event("Fillform. Command Called",
                                              str(message.chat.id),
                                              "",
                                              "")
    await fillform_command(message)

# отправляем сообщение всем пользователям от имени бота, доступно только
# админам


@botDispatcher.message_handler(commands=['sendmestoall'])
async def process_sendmestoall_command(message: types.Message):
    """
    отправляем сообщение всем пользователям от имени бота,
        доступно только админам
    """
    await get_message_to_all(message)


@botDispatcher.message_handler(state=Recording.AwaitForAMessageForAll)
async def process_callback_awaitforamessage_button(
    message: types.Message,
    state: dispatcher.FSMContext
):
    """Ввод сообщения для отправки на всех пользователей"""
    await send_message_to_all(message, state)


@botDispatcher.message_handler(commands=['feedback'])
async def process_feedback_command(message: types.Message):
    """получаем фидбек от пользователя"""
    await amplitude_send_default_source_event("Feedback. Command Called",
                                              str(message.chat.id),
                                              "",
                                              "")
    await feedback_start(message)


@botDispatcher.message_handler(state=Recording.AwaitForAFeedback)
async def send_to_admin_text(message: types.Message, state: dispatcher.FSMContext):
    """ввод сообщения фидбека от пользователя"""
    await feedback_get_text_from_user(message, state)


@botDispatcher.message_handler(content_types=types.ContentTypes.PHOTO,
                               state=Recording.AwaitForAFeedback)
async def send_to_admin_photo(message: types.Message, state: dispatcher.FSMContext):
    """добавление картинки для фидбека от пользователя"""
    await feedback_get_photo_from_user(message, state)


@botDispatcher.message_handler(commands=['feedbackanswer'])
async def process_feedback_answer_command(message: types.Message):
    """отвечаем на сообщение фидбека от пользователя, только админы"""
    await feedback_answer_start(message)


@botDispatcher.message_handler(state=Recording.AwaitForAnAnswerToFeedback)
async def send_to_user_feedback_answer_text(message: types.Message, state: dispatcher.FSMContext):
    """вводим сообщение, чтобы ответить на фидбек пользователя"""
    await feedback_send_text_to_user(message, state)


@botDispatcher.message_handler(commands=['sendmes'])
async def process_sendmes_command(message: types.Message):
    """принудительная отправка сообщения для оценки настроения за день"""
    await sendmes(message.from_user.id)


@botDispatcher.message_handler(commands=['support'])
async def process_support_command(message: types.Message):
    """вход в общение с чатом поддержки"""
    await amplitude_send_default_source_event("Support. Command Called",
                                              str(message.chat.id),
                                              "",
                                              "")
    await support_message(message)


@botDispatcher.callback_query_handler(lambda c: c.data == 'support_start')
async def support_start_dialog(callback_query: types.CallbackQuery):
    """начало чата поддержки"""
    await support_callback(callback_query)


@botDispatcher.message_handler(commands=['stop'])
async def support_stop_dialog(message: types.Message, state: dispatcher.FSMContext):
    """выход из чата поддержки"""
    await botClient.send_message(
        message.chat.id,
        (
            "Ты вышел из режима диалога с ботом. "
            "Чтобы вернуться в него снова, вызови команду /support"
        )
    )
    await amplitude_send_default_source_event("Stop. Command Called",
                                              str(message.chat.id),
                                              "",
                                              "")
    await state.finish()


@botDispatcher.message_handler(state=Recording.AwaitForAProblem)
async def chat_wait_for_a_problem(message: types.Message, state: dispatcher.FSMContext):
    """ввод проблемы для поддержки"""
    await await_for_a_problem(message, state)


@botDispatcher.message_handler(commands=['donate'])
async def donate_handler(message: types.Message):
    """команда задонатить боту, пожалуйста закиьте деньги на пончики 🙏🍩"""
    await botClient.send_message(
        message.chat.id,
        (
            "Задонатить Роджеру: https://www.tinkoff.ru/cf/2ihm5UElRfV.\n\n"
            "Деньги будут потрачены на более мощный сервер 🔥"
        ),
        disable_web_page_preview=True
    )
    await amplitude_send_default_source_event("Donate. Command Called",
                                              str(message.chat.id),
                                              "",
                                              "")


@botDispatcher.message_handler(commands=['money'])
async def money_handler(message: types.Message):
    """команда задонатить боту, пожалуйста закиьте деньги на пончики 🙏🍩"""
    await botClient.send_message(
        message.chat.id,
        (
            "Задонатить Роджеру: https://www.tinkoff.ru/cf/2ihm5UElRfV.\n\n"
            "Деньги будут потрачены на более мощный сервер 🔥"
        ),
        disable_web_page_preview=True
    )
    await amplitude_send_default_source_event("Donate. Command Called",
                                              str(message.chat.id),
                                              "",
                                              "")


# регистрация пользователя
# получаем имя пользователя


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'name_button_yes', state=Registration.Name)
async def process_callback_yesname_button1(
    callback_query: types.CallbackQuery,
    state: dispatcher.FSMContext
):
    """регистрация пользователя, имя верно - ДА"""
    await amplitude_send_default_source_event("Registration. Name Button YES Pressed",
                                              str(callback_query.from_user.id),
                                              "Name",
                                              "Button YES")
    data = await state.get_data()
    await get_user_name(data["user_id"], callback_query)
    await state.finish()
    await get_user_time_to_send(data["user_id"], callback_query.from_user.id, data["source"])


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'name_button_no', state=Registration.Name)
async def process_callback_noname_button1(
    callback_query: types.CallbackQuery,
    state: dispatcher.FSMContext
):
    """регистрация пользователя, имя верно - НЕТ"""
    await amplitude_send_default_source_event("Registration. Name Button NO Pressed",
                                              str(callback_query.from_user.id),
                                              "Name",
                                              "Button NO")
    data = await state.get_data()
    await get_printed_user_name(data["user_id"], callback_query, data["source"])


@botDispatcher.message_handler(state=Registration.AwaitForAName)
async def customer_name(message: types.Message, state: dispatcher.FSMContext):
    """регистрация пользователя, вводим имя вручную"""
    await amplitude_send_default_source_event("Registration. Name Input Success",
                                              str(message.chat.id),
                                              "",
                                              "")
    data = await state.get_data()
    username = await get_customer_name(data["user_id"], message, state, data["source"])
    if username is None:
        return
    if data["source"] == "reg":
        await get_user_time_to_send(data["user_id"], message.chat.id, "reg")


async def get_user_time_to_send(user_id: ObjectId, chat_id: int, source: str):
    """получаем время, когда отправлять сообщения пользователю"""
    await get_user_time_to_send_messages(user_id, chat_id, source)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'ask_for_time_20', state=Registration.AwaitForATimeToSend)
async def process_callback_askfortime20_button(
    callback_query: types.CallbackQuery,
    state: dispatcher.FSMContext
):
    """ввод времени для отправки сообщений, 8 вечера"""
    data = await state.get_data()
    await user_time_20(data["user_id"], callback_query, state)
    if data["source"] == "reg":
        await amplitude_send_default_source_event("Registration. TimeToSendMessages Pressed",
                                                  str(callback_query.from_user.id),
                                                  "TimeToSendMessages",
                                                  "20")
        await get_user_time_zone(data["user_id"], callback_query.from_user.id)
    if data["source"] == "settings":
        await amplitude_send_default_source_event("Settings. TimeToSendMessages Pressed",
                                                  str(callback_query.from_user.id),
                                                  "TimeToSendMessages",
                                                  "20")
        await check_to_send_mes(callback_query.from_user.id)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'ask_for_time_21', state=Registration.AwaitForATimeToSend)
async def process_callback_askfortime21_button(
    callback_query: types.CallbackQuery,
    state: dispatcher.FSMContext
):
    """ввод времени для отправки сообщений, 9 вечера"""
    data = await state.get_data()
    await user_time_21(data["user_id"], callback_query, state)
    if data["source"] == "reg":
        await amplitude_send_default_source_event("Registration. TimeToSendMessages Pressed",
                                                  str(callback_query.from_user.id),
                                                  "TimeToSendMessages",
                                                  "21")
        await get_user_time_zone(data["user_id"], callback_query.from_user.id)
    if data["source"] == "settings":
        await amplitude_send_default_source_event("Settings. TimeToSendMessages Pressed",
                                                  str(callback_query.from_user.id),
                                                  "TimeToSendMessages",
                                                  "21")
        await check_to_send_mes(callback_query.from_user.id)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'ask_for_time_22', state=Registration.AwaitForATimeToSend)
async def process_callback_askfortime22_button(
    callback_query: types.CallbackQuery,
    state: dispatcher.FSMContext
):
    """ввод времени для отправки сообщений, 10 вечера"""
    data = await state.get_data()
    await user_time_22(data["user_id"], callback_query, state)
    if data["source"] == "reg":
        await amplitude_send_default_source_event("Registration. TimeToSendMessages Pressed",
                                                  str(callback_query.from_user.id),
                                                  "TimeToSendMessages",
                                                  "22")
        await get_user_time_zone(data["user_id"], callback_query.from_user.id)
    if data["source"] == "settings":
        await amplitude_send_default_source_event("Settings. TimeToSendMessages Pressed",
                                                  str(callback_query.from_user.id),
                                                  "TimeToSendMessages",
                                                  "22")
        await check_to_send_mes(callback_query.from_user.id)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'ask_for_time_23', state=Registration.AwaitForATimeToSend)
async def process_callback_askfortime23_button1(
    callback_query: types.CallbackQuery,
    state: dispatcher.FSMContext
):
    """ввод времени для отправки сообщений, 11 вечера"""
    data = await state.get_data()
    await user_time_23(data["user_id"], callback_query, state)
    if data["source"] == "reg":
        await amplitude_send_default_source_event("Registration. TimeToSendMessages Pressed",
                                                  str(callback_query.from_user.id),
                                                  "TimeToSendMessages",
                                                  "23")
        await get_user_time_zone(data["user_id"], callback_query.from_user.id)
    if data["source"] == "settings":
        await amplitude_send_default_source_event("Settings. TimeToSendMessages Pressed",
                                                  str(callback_query.from_user.id),
                                                  "TimeToSendMessages",
                                                  "23")
        await check_to_send_mes(callback_query.from_user.id)


async def get_user_time_zone(user_id: ObjectId, chat_id: int):
    """получаем таймзону пользователя"""
    await get_user_timezone(user_id, chat_id, "reg")


@botDispatcher.message_handler(state=Registration.AwaitForATimeZoneToSend)
async def customer(message: types.Message, state: dispatcher.FSMContext):
    """запрашиваем таймзону"""
    data = await state.get_data()
    time_zone = await customer_timezone(data["user_id"], message, state, data["source"])
    if time_zone is not None and data["source"] == "reg":
        await amplitude_send_default_source_event("Registration. Timezone Input Success",
                                                  str(message.chat.id),
                                                  "TimezoneInput",
                                                  "")
        await state.finish()
        update_user_is_active(data["user_id"], True)
        await botClient.send_message(message.chat.id,
                                     "Отлично! 😍")
        await create_new_message_after_registration(data["user_id"], message.chat.id)
    if data["source"] == "settings":
        await amplitude_send_default_source_event("Settings. Timezone Changed Success",
                                                  str(message.chat.id),
                                                  "",
                                                  "")
        await botClient.send_message(message.chat.id,
                                     "Обновил твой часовой пояс на UTC" + time_zone)
        await check_to_send_mes(message.chat.id)
        await state.finish()


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'rate_good', state='*')
async def process_callback_rategood_button(callback_query: types.CallbackQuery):
    """оценка сообщения от пользователя - лайк"""
    await rate_message(callback_query, True)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'rate_bad', state='*')
async def process_callback_ratebad_button(callback_query: types.CallbackQuery):
    """оценка сообщения от пользователя - дизлайк"""
    await rate_message(callback_query, False)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'rate_good_support', state='*')
async def process_support_callback_rategood_button(callback_query: types.CallbackQuery):
    """оценка сообщения поддержки - лайк"""
    await callback_after_click_on_button_support(callback_query, True)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'rate_bad_support', state='*')
async def process_support_callback_ratebad_button(callback_query: types.CallbackQuery):
    """оценка сообщения поддержки - дизлайк"""
    await callback_after_click_on_button_support(callback_query, False)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'green_button_answer', state='*')
async def process_callback_greenbutton_button4(callback_query: types.CallbackQuery):
    """оценка настроения за день - зелёный"""
    await callback_after_click_on_color_button(callback_query, 4, 'green')


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'yellow_button_answer', state='*')
async def process_callback_yellowbutton_button3(callback_query: types.CallbackQuery):
    """оценка настроения за день - жёлтый"""
    await callback_after_click_on_color_button(callback_query, 3, 'yellow')


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'orange_button_answer', state='*')
async def process_callback_orangebutton_button2(callback_query: types.CallbackQuery):
    """оценка настроения за день - оранжевый"""
    await callback_after_click_on_color_button(callback_query, 2, 'orange')


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'red_button_answer', state='*')
async def process_callback_redbutton_button1(callback_query: types.CallbackQuery):
    """оценка настроения за день - красный"""
    await callback_after_click_on_color_button(callback_query, 1, 'red')


@botDispatcher.message_handler(commands=['settings'])
async def settings_main_command(message: types.Message):
    """update user settings by themselves"""
    await amplitude_send_default_source_event("Settings. Command Called",
                                              str(message.chat.id),
                                              "",
                                              "")
    await settings_main(message.chat.id)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'settings_name')
async def settings_change_name_callback(callback_query: types.CallbackQuery):
    """update user name by themselves"""
    await amplitude_send_default_source_event("Settings. Name Change Pressed",
                                              str(callback_query.from_user.id),
                                              "Change Name",
                                              "")
    user = get_user_by_telegram_id(str(callback_query.from_user.id))
    await get_printed_user_name(user["_id"], callback_query, "settings")


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'settings_timezone')
async def settings_change_timezone_callback(callback_query: types.CallbackQuery):
    """update user timezone by themselves"""
    await amplitude_send_default_source_event("Settings. Timezone Change Pressed",
                                              str(callback_query.from_user.id),
                                              "Change Timezone",
                                              "")
    user = get_user_by_telegram_id(str(callback_query.from_user.id))
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await get_user_timezone(user["_id"], callback_query.from_user.id, "settings")


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'settings_time_to_send_messages_button')
async def settings_change_time_to_send_messages_callback(callback_query: types.CallbackQuery):
    """update time to send messages by themselves"""
    await amplitude_send_default_source_event("Settings. TimeToSendMessages Change Pressed",
                                              str(callback_query.from_user.id),
                                              "Change Time To Send Messages",
                                              "")
    user = get_user_by_telegram_id(str(callback_query.from_user.id))
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await get_user_time_to_send_messages(user["_id"], callback_query.from_user.id, "settings")


@botDispatcher.message_handler(commands=['sendnewyearstata'])
async def sendnewyearstata_command(message: types.Message):
    """sending new year messages to all active users"""
    await send_new_year_message(str(message.chat.id))


@botDispatcher.message_handler(commands=['newyearstata'])
async def newyearstata_command(message: types.Message):
    """sending new year stata by command"""
    user = get_user_by_telegram_id(str(message.chat.id))

    current_year = datetime.now().year

    await botClient.send_message(
        message.chat.id,
        "Твоя статистика за " + str(current_year) + " год готова!\n\nПереходи по ссылке: " +
        "https://rogerbot.tech/2024/" +
        str(user["_id"]), disable_web_page_preview=True
    )


@botDispatcher.message_handler(content_types='text', state='*')
async def process_any_command(message: types.Message):
    """дефолтная обработка любого сообщения"""
    await botClient.send_message(
        message.chat.id,
        "Не знаю эту команду. Попробуй написать что-нибудь другое"
    )
    await amplitude_send_default_source_event("Unknown Command Called",
                                              str(message.chat.id),
                                              message.text,
                                              "")


if __name__ == "__main__":
    logger.info('LET\'S FUCKING GOOOOOOOOOOO!')
    executor.start_polling(botDispatcher)
