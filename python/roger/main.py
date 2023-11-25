import json

from aiogram.utils import executor
from aiogram import types, dispatcher
from aiogram.utils.callback_data import CallbackData

from logger import logger
from states import Recording, FriendsStates, Registration
from common import check_id_username_is_valid_before_save, delete_keyboard
from database import create_new_user
from feedback import feedback_start, feedback_get_text_from_user, feedback_get_photo_from_user
from version import version_command
from restart import restart_command
from sendmestoall import send_message_to_all, get_message_to_all
from start import start_command
from reg.reg_user_name import get_user_name, get_printed_user_name, get_customer_name
from reg.reg_user_time import get_user_time_to_send_messages, user_time_20, user_time_21, user_time_22, user_time_23
from reg.reg_user_timezone import get_user_timezone, customer_timezone
from stata import stata_show_mes, delete_from_cart_handler1
from ratestata import send_rate_stata, get_rate_stata
from sendmessage import sendmes, callback_after_click_on_color_button
from variables import botClient, botDispatcher
from handlers import rate_message
from fillform import fillform_command
from feedback_answer import feedback_answer_start, feedback_send_text_to_user
from chatgpt import support_message, await_for_a_problem, callback_after_click_on_button_support, support_callback
from friends import get_friend_nickname, get_menu_for_command, show_active_friends, show_info, watch_friends_internal_requests, send_request_to_a_friend, friends_internal_request, call_back_approve, delete_friends, delete_friends_message


# текущая версия бота
version = "1.4.0"

# read texts from json file
with open('texts.json', encoding="utf-8") as t:
    texts = json.load(t)

# команда старт при первом запуске бота


@botDispatcher.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await start_command(message)

# команда по отслеживанию, является ли пользак активным
# @botDispatcher.message_handler()
# async def process_start_command(message: types.Message):
#     is_active = await is_user_active(message.chat.id)
#     if (is_active == True):
#         print ('is_active')
#         return
#     else:
#         #тут отправить на степ знакомства, на котором пользователь отвалился в прошлый раз
#         print (1)
#         return 1 #пока просто базовая заглушка

# версия бота


@botDispatcher.message_handler(commands=['version'])
async def process_version_command(message: types.Message):
    await version_command(message, version)

# Перезагрузка ботов


@botDispatcher.message_handler(commands=['restart'])
async def process_restart_command(message: types.Message):
    await restart_command(message)


@botDispatcher.message_handler(commands=['friends'])
async def friends_command(message: types.Message):
    await get_menu_for_command(message.chat.id)


@botDispatcher.callback_query_handler(lambda c: c.data == 'main', state='*')
async def any_state_main_handler(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await state.finish()
    await botClient.answer_callback_query(callback_query.id, text='Ты вышел из прошлого режима, можешь выбрать другой 😌')


@botDispatcher.callback_query_handler(lambda c: c.data == 'friends_menu')
async def show_menu(callback_query: types.CallbackQuery):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await get_menu_for_command(callback_query.from_user.id)


@botDispatcher.callback_query_handler(lambda c: c.data == 'add_friends')
async def add_friends_handler(callback_query: types.CallbackQuery):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Выбрать контакт",
                 request_user=types.KeyboardButtonRequestUser(1, user_is_bot=False)))
    await botClient.send_message(callback_query.from_user.id, "Выбери контакт в Telegram, который хочешь добавить в друзья", reply_markup=keyboard)
    await Recording.AwaitForAFriendContact.set()


@botDispatcher.message_handler(content_types=types.ContentType.USER_SHARED,
                               state=Recording.AwaitForAFriendContact)
async def contacts(msg: types.Message, state: dispatcher.FSMContext):
    await msg.answer("Вычисляю, знаком ли я с твоим другом...", reply_markup=types.ReplyKeyboardRemove())
    await send_request_to_a_friend(msg)
    await state.finish()


@botDispatcher.callback_query_handler(
    call_back_approve.filter(id='friend_approve'))
async def process_callback_friend_request_approve_button(callback_query: types.CallbackQuery, callback_data: dict):
    friend = callback_data.get("friend")
    await friends_internal_request(callback_query, friend, True)


@botDispatcher.callback_query_handler(lambda c: c.data == 'friend_decline')
async def process_callback_friend_request_decline_button(callback_query: types.CallbackQuery, callback_data: dict):
    friend = callback_data.get("friend")
    await friends_internal_request(callback_query, friend, False)


@botDispatcher.callback_query_handler(lambda c: c.data == 'friend_delete')
async def process_callback_friend_request_delete_button(callback_query: types.CallbackQuery, callback_data: dict):
    # передай норм данные в функцию, чё это такое, бро
    await delete_friends_message(1, [], 1, 1)


@botDispatcher.message_handler(
    state=FriendsStates.AwaitForAFriendNicknameToAdd)
async def process_callback_await_for_a_message_button(message: types.Message, state: dispatcher.FSMContext):
    await get_friend_nickname(message, state)


@botDispatcher.callback_query_handler(lambda c: c.data == 'check_friend_list')
async def friends_list_handler(callback_query: types.CallbackQuery):
    await show_active_friends(callback_query)


@botDispatcher.callback_query_handler(lambda c: c.data == 'info_friend_list')
async def friends_info_handler(callback_query: types.CallbackQuery):
    await show_info(callback_query)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'delete_from_friends')
async def delete_friends_handler(callback_query: types.CallbackQuery):
    await delete_friends(callback_query)


@botDispatcher.callback_query_handler(lambda c: c.data == 'friends_requests')
async def friends_request_handler(callback_query: types.CallbackQuery):
    await watch_friends_internal_requests(callback_query.from_user.id, callback_query.message.message_id, True)


@botDispatcher.message_handler(commands=['friends_requests'])
async def friends_request_command(message: types.Message):
    await watch_friends_internal_requests(message.chat.id, message.message_id, False)

# вывод статистики по созданному пользователем сообщению
# колбек для обработки статистики по сообщению пользователя
cart_cb = CallbackData("q", "id", "button_parameter")

# вывод статистики по созданному пользователем сообщению
# колбек для обработки статистики по сообщению пользователя
cart_cb = CallbackData("q", "id", "button_parameter")


@botDispatcher.message_handler(commands=['stata'])
async def process_stata_command(message: types.Message):
    await botClient.send_message(message.chat.id, "Произвожу вычисления, немного терпения 😌")
    await stata_show_mes(message)


@botDispatcher.callback_query_handler(
    cart_cb.filter(button_parameter=["kb_mes"]))
async def delete_from_cart_handler(call: types.CallbackQuery, callback_data: dict):
    await botClient.send_message(call.from_user.id, "Подгружаю статистику, немного терпения")
    await delete_from_cart_handler1(call, callback_data)


# вывод статистики по настроению пользователя
# колбек для обработки статистики по настроению пользователя
cart_cb = CallbackData("q", "id", "button_parameter")


@botDispatcher.message_handler(commands=['mentalstata'])
async def process_rate_stata_command(message: types.Message):
    await get_rate_stata(message)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'month', state=Recording.AwaitForARateStata)
async def rate_stata_handler_month(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    await state.finish()
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await send_rate_stata(callback_query.from_user.id, 'month')


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'week2', state=Recording.AwaitForARateStata)
async def rate_stata_handler_week2(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    await state.finish()
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await send_rate_stata(callback_query.from_user.id, 'week2')


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'week', state=Recording.AwaitForARateStata)
async def rate_stata_handler_week(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    await state.finish()
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await send_rate_stata(callback_query.from_user.id, 'week')

# заполняем форму по команде


@botDispatcher.message_handler(commands=['fillform'])
async def process_fillform_command(message: types.Message):
    await fillform_command(message)

# отправляем сообщение всем пользователям от имени бота, доступно только
# админам


@botDispatcher.message_handler(commands=['sendmestoall'])
async def process_sendmestoall_command(message: types.Message):
    await get_message_to_all(message)


@botDispatcher.message_handler(state=Recording.AwaitForAMessageForAll)
async def process_callback_awaitforamessage_button(message: types.Message, state: dispatcher.FSMContext):
    await send_message_to_all(message, state)

# получаем фидбек от пользователя


@botDispatcher.message_handler(commands=['feedback'])
async def process_feedback_command(message: types.Message):
    await feedback_start(message)


@botDispatcher.message_handler(state=Recording.AwaitForAFeedback)
async def send_to_admin_text(message: types.Message, state: dispatcher.FSMContext):
    await feedback_get_text_from_user(message, state)


@botDispatcher.message_handler(content_types=types.ContentTypes.PHOTO,
                               state=Recording.AwaitForAFeedback)
async def send_to_admin_photo(message: types.Message, state: dispatcher.FSMContext):
    await feedback_get_photo_from_user(message, state)


@botDispatcher.message_handler(commands=['feedbackanswer'])
async def process_feedback_answer_command(message: types.Message):
    await feedback_answer_start(message)


@botDispatcher.message_handler(state=Recording.AwaitForAnAnswerToFeedback)
async def send_to_user_feedback_answer_text_1(message: types.Message, state: dispatcher.FSMContext):
    await feedback_send_text_to_user(message, state)

# принудительная отправка сообщения для оценки настроения за день


@botDispatcher.message_handler(commands=['sendmes'])
async def process_sendmes_command(message: types.Message):
    await sendmes(message.from_user.id)


@botDispatcher.message_handler(commands=['support'])
async def process_support_command(message: types.Message):
    await support_message(message)


@botDispatcher.callback_query_handler(lambda c: c.data == 'support_start')
async def support_start_dialog(callback_query: types.CallbackQuery):
    await support_callback(callback_query)


@botDispatcher.message_handler(commands=['stop'])
async def support_stop_dialog(message: types.Message, state: dispatcher.FSMContext):
    await botClient.send_message(message.chat.id, "Ты вышел из режима диалога с ботом. Чтобы вернуться в него снова, вызови команду /support")
    await state.finish()


@botDispatcher.message_handler(state=Recording.AwaitForAProblem)
async def send_to_user_feedback_answer_text(message: types.Message, state: dispatcher.FSMContext):
    await await_for_a_problem(message, state)


@botDispatcher.message_handler(commands=['donate'])
async def donate_handler(message: types.Message):
    await botClient.send_message(message.chat.id, "Задонатить Роджеру: https://www.tinkoff.ru/cf/9KODrlaoPCR. Деньги будут потрачены на более мощный сервер 🔥", disable_web_page_preview=True)

# регистрация пользователя
# получаем имя пользователя


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'name_button_yes', state=Registration.Name)
async def process_callback_yesname_button1(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    global user_name
    user_name = await get_user_name(callback_query, state)
    await get_user_time_to_send(callback_query.from_user.id)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'name_button_no', state=Registration.Name)
async def process_callback_noname_button1(callback_query: types.CallbackQuery):
    await get_printed_user_name(callback_query)


@botDispatcher.message_handler(state=Registration.AwaitForAName)
async def customer_name(message: types.Message, state: dispatcher.FSMContext):
    global user_name
    user_name = await get_customer_name(message, state)
    if user_name is None:
        return
    await get_user_time_to_send(message.chat.id)


# получаем время, когда отправлять сообщения пользователю
async def get_user_time_to_send(chat_id: int):
    await get_user_time_to_send_messages(chat_id)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'ask_for_time_20', state=Registration.AwaitForATimeToSend)
async def process_callback_askfortime20_button(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    global user_time
    user_time = await user_time_20(callback_query, state)
    await get_user_time_zone(callback_query.from_user.id)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'ask_for_time_21', state=Registration.AwaitForATimeToSend)
async def process_callback_askfortime21_button(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    global user_time
    user_time = await user_time_21(callback_query, state)
    await get_user_time_zone(callback_query.from_user.id)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'ask_for_time_22', state=Registration.AwaitForATimeToSend)
async def process_callback_askfortime22_button(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    global user_time
    user_time = await user_time_22(callback_query, state)
    await get_user_time_zone(callback_query.from_user.id)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'ask_for_time_23', state=Registration.AwaitForATimeToSend)
async def process_callback_askfortime23_button1(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    global user_time
    user_time = await user_time_23(callback_query, state)
    await get_user_time_zone(callback_query.from_user.id)


# получаем таймзону пользователя
async def get_user_time_zone(chat_id: int):
    await get_user_timezone(chat_id)


@botDispatcher.message_handler(state=Registration.AwaitForATimeZoneToSend)
async def customer(message: types.Message, state: dispatcher.FSMContext):
    global time_zone
    time_zone = await customer_timezone(message, state)
    if time_zone is not None:
        await create_user(message)


async def create_user(message: types.Message):
    await create_new_user(await check_id_username_is_valid_before_save(message.from_user.username), user_name, time_zone, str(message.chat.id), user_time)

# оценки
# получаем оценку сообщения от пользователя


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'rate_good', state='*')
async def process_callback_rategood_button(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    await rate_message(callback_query, state, True)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'rate_bad', state='*')
async def process_callback_ratebad_button(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    await rate_message(callback_query, state, False)

# получаем оценку ChatGPT от пользователя


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'rate_good_support', state='*')
async def process_support_callback_rategood_button(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    await callback_after_click_on_button_support(callback_query, True)


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'rate_bad_support', state='*')
async def process_support_callback_ratebad_button(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    await callback_after_click_on_button_support(callback_query, False)

# оценка настроения за день


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'green_button_answer', state='*')
async def process_callback_greenbutton_button4(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    await callback_after_click_on_color_button(callback_query, state, 4, 'green')


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'yellow_button_answer', state='*')
async def process_callback_yellowbutton_button3(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    await callback_after_click_on_color_button(callback_query, state, 3, 'yellow')


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'orange_button_answer', state='*')
async def process_callback_orangebutton_button2(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    await callback_after_click_on_color_button(callback_query, state, 2, 'orange')


@botDispatcher.callback_query_handler(lambda c: c.data ==
                                      'red_button_answer', state='*')
async def process_callback_redbutton_button1(callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    await callback_after_click_on_color_button(callback_query, state, 1, 'red')

# дефолтная обработка любого сообщения


@botDispatcher.message_handler(content_types='text', state='*')
async def process_any_command(message: types.Message):
    await botClient.send_message(message.chat.id, "Не знаю эту команду. Попробуй написать что-нибудь другое")


if __name__ == "__main__":
    logger.info('LET\'S FUCKING GOOOOOOOOOOO!')
    executor.start_polling(botDispatcher)
