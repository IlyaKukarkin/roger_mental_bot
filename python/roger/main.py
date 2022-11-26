import json

import asyncio
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData

from states import Recording
from common import check_id_username_is_valid_before_save, delete_keyboard
from database import create_new_user
from feedback import feedback_command, feedback_get_text_from_user, feedback_get_photo_from_user
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
from on_startup import enable_task_to_send_mes
from config import dp, bot
from handlers import rate_message
from fillform import fillform_command

#текущая версия бота
version = "1.0.5"


# read texts from json file
with open('texts.json') as t:
    texts = json.load(t)


#команда старт при первом запуске бота
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await start_command(message)


#версия бота
@dp.message_handler(commands=['version'])
async def process_version_command(message: types.Message):
    await version_command(message, version)

#Перезагрузка ботов
@dp.message_handler(commands=['restart'])
async def process_restart_command(message: types.Message):
    await restart_command(message)

#тестовая команда
@dp.message_handler(commands=['test'])
async def process_start_command(message: types.Message):
    await bot.send_message(message.chat.id, "Меня не тестили, сорри!")

#вывод статистики по созданному пользователем сообщению
#колбек для обработки статистики по сообщению пользователя
cart_cb = CallbackData("q", "id", "button_parameter")

#вывод статистики по созданному пользователем сообщению
#колбек для обработки статистики по сообщению пользователя
cart_cb = CallbackData("q", "id", "button_parameter")

@dp.message_handler(commands=['stata'])
async def process_stata_command(message: types.Message):
    await bot.send_message(message.chat.id, "Произвожу вычисления, немного терпения 😌")
    await stata_show_mes(message)

@dp.callback_query_handler(cart_cb.filter(button_parameter=["kb_mes"]))
async def delete_from_cart_handler(call: CallbackQuery, callback_data: dict):
    await bot.send_message(call.from_user.id, "Подгружаю статистику, немного терпения")
    await delete_from_cart_handler1(call, callback_data)


#вывод статистики по настроению пользователя
#колбек для обработки статистики по настроению пользователя
cart_cb = CallbackData("q", "id", "button_parameter")

@dp.message_handler(commands=['mentalstata'])
async def process_rate_stata_command(message: types.Message):
    await get_rate_stata(message)

@dp.callback_query_handler(lambda c: c.data == 'month', state=Recording.AwaitForARateStata)
async def rate_stata_handler_month(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await send_rate_stata(callback_query.from_user.id, 'month')

@dp.callback_query_handler(lambda c: c.data == 'week2', state=Recording.AwaitForARateStata)
async def rate_stata_handler_week2(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await send_rate_stata(callback_query.from_user.id, 'week2')

@dp.callback_query_handler(lambda c: c.data == 'week', state=Recording.AwaitForARateStata)
async def rate_stata_handler_week(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await send_rate_stata(callback_query.from_user.id, 'week')

#заполняем форму по команде
@dp.message_handler(commands=['fillform'])
async def process_fillform_command(message: types.Message):
    await fillform_command (message)

#отправляем сообщение всем пользователям от имени бота, доступно только админам
@dp.message_handler(commands=['sendmestoall'])
async def process_sendmestoall_command(message: types.Message):
    await get_message_to_all(message)

@dp.message_handler(state=Recording.AwaitForAMessageForAll)
async def process_callback_awaitforamessage_button(message: types.Message, state: FSMContext):
    await send_message_to_all(message, state)


#получаем фидбек от пользователя
@dp.message_handler(commands=['feedback'])
async def process_feedback_command(message: types.Message):
    await feedback_command(message)

@dp.message_handler(state=Recording.AwaitForAFeedback)
async def send_to_admin_text(message: types.Message, state: FSMContext):
    await feedback_get_text_from_user(message, state)

@dp.message_handler(content_types=types.ContentTypes.PHOTO, state=Recording.AwaitForAFeedback)
async def send_to_admin_photo(message: types.Message, state: FSMContext):
    await feedback_get_photo_from_user(message, state)


#принудительная отправка сообщения для оценки настроения за день
@dp.message_handler(commands=['sendmes'])
async def process_sendmes_command(message: types.Message):
    await sendmes(message.from_user.id)


#регистрация пользователя
#получаем имя пользователя
@dp.callback_query_handler(lambda c: c.data == 'name_button_yes', state=Recording.Name)
async def process_callback_yesname_button1(callback_query: types.CallbackQuery, state: FSMContext):
    global user_name 
    user_name = await get_user_name(callback_query, state)
    await get_user_time_to_send(callback_query.from_user.id)

@dp.callback_query_handler(lambda c: c.data == 'name_button_no', state=Recording.Name)
async def process_callback_noname_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await get_printed_user_name(callback_query, state)

@dp.message_handler(state=Recording.AwaitForAName)
async def customer_name(message: types.Message, state: FSMContext):
    global user_name 
    user_name = await get_customer_name(message, state)
    await get_user_time_to_send(message.chat.id)


#получаем время, когда отправлять сообщения пользователю
async def get_user_time_to_send(chat_id: int):
    await get_user_time_to_send_messages(chat_id)

@dp.callback_query_handler(lambda c: c.data == 'ask_for_time_20', state=Recording.AwaitForATimeToSend)
async def process_callback_askfortime20_button(callback_query: types.CallbackQuery, state: FSMContext):
    global user_time
    user_time = await user_time_20(callback_query, state)
    await get_user_time_zone(callback_query.from_user.id)

@dp.callback_query_handler(lambda c: c.data == 'ask_for_time_21', state=Recording.AwaitForATimeToSend)
async def process_callback_askfortime21_button(callback_query: types.CallbackQuery, state: FSMContext):
    global user_time
    user_time = await user_time_21(callback_query, state)
    await get_user_time_zone(callback_query.from_user.id)

@dp.callback_query_handler(lambda c: c.data == 'ask_for_time_22', state=Recording.AwaitForATimeToSend)
async def process_callback_askfortime22_button(callback_query: types.CallbackQuery, state: FSMContext):
    global user_time
    user_time = await user_time_22(callback_query, state)
    await get_user_time_zone(callback_query.from_user.id)

@dp.callback_query_handler(lambda c: c.data == 'ask_for_time_23', state=Recording.AwaitForATimeToSend)
async def process_callback_askfortime23_button1(callback_query: types.CallbackQuery, state: FSMContext):
    global user_time
    user_time = await user_time_23(callback_query, state)
    await get_user_time_zone(callback_query.from_user.id)


#получаем таймзону пользователя
async def get_user_time_zone(chat_id: int):
    await get_user_timezone(chat_id)

@dp.message_handler(state=Recording.AwaitForATimeZoneToSend)
async def customer(message: types.Message, state: FSMContext):
    global time_zone
    time_zone = await customer_timezone(message, state)
    if time_zone != None:
        await create_user (message)

async def create_user (message: types.Message):
    await create_new_user(await check_id_username_is_valid_before_save(message.from_user.username), user_name, time_zone, str(message.chat.id), user_time)

#оценки
#получаем оценку сообщения от пользователя
@dp.callback_query_handler(lambda c: c.data == 'rate_good')
async def process_callback_rategood_button(callback_query: types.CallbackQuery, state: FSMContext):
    await rate_message(callback_query, state, True)

@dp.callback_query_handler(lambda c: c.data == 'rate_bad')
async def process_callback_ratebad_button(callback_query: types.CallbackQuery, state: FSMContext):
    await rate_message(callback_query, state, False)

#оценка настроения за день
@dp.callback_query_handler(lambda c: c.data == 'green_button_answer')
async def process_callback_greenbutton_button4(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_after_click_on_color_button(callback_query, state, 4, 'green')

@dp.callback_query_handler(lambda c: c.data == 'yellow_button_answer')
async def process_callback_yellowbutton_button3(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_after_click_on_color_button(callback_query, state, 3, 'yellow')

@dp.callback_query_handler(lambda c: c.data == 'orange_button_answer')
async def process_callback_orangebutton_button2(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_after_click_on_color_button(callback_query, state, 2, 'orange')

@dp.callback_query_handler(lambda c: c.data == 'red_button_answer')
async def process_callback_redbutton_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_after_click_on_color_button(callback_query, state, 1, 'red')

#дефолтный запуск
#запускаем второй поток для отправки сообщений раз в сутки
async def set_task_to_send_messages(x):
    asyncio.create_task(enable_task_to_send_mes())

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=set_task_to_send_messages)
