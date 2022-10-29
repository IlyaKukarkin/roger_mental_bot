from sqlite3 import Cursor
import json
import random
import time
import os
import urllib.parse

import asyncio
import requests
import datetime
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, types
from aiogram.utils.markdown import bold, text
from aiogram.types import ParseMode, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bson import ObjectId
from states import Recording
from keyboards import kb_for_mental_poll, ask_for_name_kb, ask_for_rate_messages, ask_for_time_to_send_kb
from common import delete_keyboard
from database import get_database
from aiogram.utils.callback_data import CallbackData
import pytz

# tokens
# token_bot = os.getenv("TOKEN_ROGER_PROD_BOT")
token_bot = os.getenv("TOKEN_BOT")
db_token = os.getenv("MONGODB_URI")
link_to_form = os.getenv("LINK_TO_FORM")
contenful_access_token = os.getenv("CONTENTFUL_ACCESS_TOKEN")
contenful_space_id = os.getenv("CONTENTFUL_SPACE_ID")
contentful_api_readonly_url = os.getenv("CONTENTFUL_API_READONLY_URL")
cuttly_api_key = os.getenv("CUTTLY_API_KEY")

# read texts from json file
with open('texts.json') as t:
    texts = json.load(t)

bot = Bot(token=token_bot)
dp = Dispatcher(bot, storage=MemoryStorage())
cart_cb = CallbackData("q", "id", "button_parameter")


async def kb_for_stata(messages: Cursor):
    kb_stata_messages = InlineKeyboardMarkup(row_width=1)
    for item in messages:
        i = InlineKeyboardButton(text=str(item['text'])[:30], callback_data=cart_cb.new(
            (str(item["_id"])), button_parameter="kb_mes"))
        kb_stata_messages.add(i)
    return kb_stata_messages


@dp.message_handler(commands=['stata'])
async def process_feedback_command(message: types.Message):
    collection_name = get_database()
    user = collection_name["users"].find_one(
        {"telegram_id": str(message.chat.id)}, {'_id': 1, "form_id": 1})
    messages = collection_name["messages"].find({"id_user": user["_id"]}, {
                                                "_id": 1, "text": 1, "media_link": 1, "is_approved": 1, "image_ids": 1, "is_anonymous": 1, "created_at": 1})
    length = len(list(messages.clone()))
    if (length == 0):
        await bot.send_message(message.chat.id, "У тебя нет созданных сообщений. Как насчет сделать первое?\n\n" + link_to_form + str(user['form_id']))
        return
    elif (length == 1):
        await send_stata(str(messages[0]["_id"]))
        return
    elif (length > 1):
        await bot.send_message(message.chat.id, "Выбери сообщение, по которому хочешь увидеть статистику", reply_markup=await kb_for_stata(messages))
    collection_name['users'].find().close()
    collection_name['messages'].find().close()


@dp.callback_query_handler(cart_cb.filter(button_parameter=["kb_mes"]))
async def delete_from_cart_handler(call: CallbackQuery, callback_data: dict):
    id_message = callback_data.get("id")
    await delete_keyboard(call.from_user.id, call.message.message_id)
    await send_stata(id_message)


async def send_stata(id_message: str):
    collection_name = get_database()
    message = collection_name["messages"].find_one(
        {"_id": ObjectId(id_message)})
    count_times = collection_name["user_messages"].find(
        {"id_message": message["_id"]}, {"_id": 1})

    is_approved = message["is_approved"] == True and 'true' or 'false'

    count_rates = collection_name["rate"].aggregate(
        [
            {
                '$match': {
                    'id_message': message["_id"]
                }
            }, {
                '$group': {
                    '_id': '$rate',
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ]
    )

    good_rates = 0
    bad_rates = 0

    for rate in count_rates:
        if (rate['_id'] == True):
            good_rates = rate['count']
        else:
            bad_rates = rate['count']

    print(message)

    user = collection_name["users"].find_one(
        {"_id": message["id_user"]}, {'telegram_id': 1})

    # show=5&likes=3&dislikes=2&approved=true&link_clicks=3&current_date=2022-10-28T13:55:46.918+00:00&text=SUUUUUUUIIIII&link=https://youtube.com/shorts/IX51UAJUhhQ?feature=share&image=https://images.ctfassets.net/n1wrmpzswxf2/48uznlXxRp2f2kOF8sBzm/6ea1cb1acacf7077fe14e5d9aa95f536/image-0&created_date=2022-10-23T13:55:46.918+00:00
    image_url = f"?show={str(len(list(count_times)))}&likes={good_rates}&dislikes={bad_rates}&approved={is_approved}&current_date={datetime.datetime.now(pytz.utc).isoformat()}&text={urllib.parse.quote(message['text'])}&created_date={message['created_date'].isoformat()}"

    if (message['media_link'] != ''):
        response = requests.get('http://cutt.ly/api/api.php?key=' +
                                cuttly_api_key + '&stats=' + message['media_link'])
        answer = json.loads(response.content)
        link_cliks = answer['stats']['clicks']

        image_url = image_url + f"&link_clicks={link_cliks}&link={urllib.parse.quote(message['original_media_link'])}"

    if (len(message['image_ids']) != 0):
        image = await get_pictures(message['image_ids'][0])

        image_url = image_url + f"&image={urllib.parse.quote('https://' + image)}"

    result_image_url = 'https://roger-mental-ai6381us5-ilyakukarkin.vercel.app/api/message-stats' + image_url

    print(result_image_url)

    await bot.send_photo(int(user["telegram_id"]), result_image_url)

    collection_name['messages'].find().close()
    collection_name['user_messages'].find().close()
    collection_name['rate'].find().close()
    collection_name['users'].find().close()


@dp.message_handler(commands=['feedback'])
async def process_feedback_command(message: types.Message):
    await bot.send_message(message.chat.id, "Отправь любое сообщение (текст или фото) — и я перешлю его разработчикам")
    await Recording.AwaitForAFeedback.set()


@dp.message_handler(state=Recording.AwaitForAFeedback)
async def process_callback_button1(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    collection_name = get_database()
    admins = collection_name["users"].find({"is_admin": True, "is_active": True}, {
                                           '_id': 0, 'telegram_id': 1})
    for id in admins:
        user = collection_name["users"].find_one(
            {'telegram_id': str(message.chat.id)}, {'telegram_username': 1})
        await bot.send_message(id["telegram_id"], "Новый фидбек от пользователя " + user['telegram_username'] + ' из RogerBot. Вот, что он пишет: \n\n"' + message.text + '"')
    await bot.send_message(message.chat.id, "Сообщение улетело разработчикам. Спасибо! 😍")
    await state.finish()
    collection_name['users'].find().close()


@dp.message_handler(content_types=types.ContentTypes.PHOTO, state=Recording.AwaitForAFeedback)
async def send_to_admin(message: types.Message, state: FSMContext):
    collection_name = get_database()
    admins = collection_name["users"].find({"is_admin": True, "is_active": True}, {
                                           '_id': 0, 'telegram_id': 1})
    for id in admins:
        user = collection_name["users"].find_one(
            {'telegram_id': str(message.chat.id)}, {'telegram_username': 1})
        await bot.send_message(id['telegram_id'], "Новое фото от пользователя " + user['telegram_username'] + '. Вот оно:')
        await bot.send_photo(id['telegram_id'], photo=message.photo[-1].file_id)
    await bot.send_message(message.chat.id, "Сообщение улетело разработчикам. Спасибо! 😍")
    await state.finish()
    collection_name['users'].find().close()


@dp.message_handler(commands=['sendmes'])
async def process_start_command(message: types.Message):
    try:
        collection_name = get_database()
        user = collection_name["users"].find_one(
            {"telegram_id": str(message.chat.id)}, {'_id': 1, 'id_user': 1})
        id_previous_mes = collection_name['mental_rate'].find_one(
            {"rate": 0, "id_user": user['_id']}, {'id_tg_message': 1}, sort=[("date", -1)])
        if (id_previous_mes != None):
            await delete_keyboard(message.chat.id, id_previous_mes['id_tg_message'])
        id = await bot.send_message(message.chat.id, await get_options('polls_questions'), parse_mode=ParseMode.MARKDOWN, reply_markup=kb_for_mental_poll)
        collection_name['mental_rate'].insert_one(
            {"rate": 0, "id_user": user['_id'], "date": datetime.datetime.now(), "id_tg_message": id.message_id})
        collection_name['users'].find().close()
        collection_name['mental_rate'].find().close()
    except (Exception):
        await bot.send_message(message.chat.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори отправку настроения через несколько минут или напиши разработчикам через команду /feedback")


@dp.callback_query_handler(lambda c: c.data == 'green_button_answer')
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    try:
        collection_name = get_database()
        user = collection_name["users"].find_one(
            {"telegram_id": str(callback_query.from_user.id)}, {'_id': 1, 'name': 0})
        collection_name['mental_rate'].find_one_and_update({"$and": [{"id_user": user["_id"]}, {
                                                           "id_tg_message": callback_query.message.message_id}]}, {"$set": {"rate": 4}})
        await get_options_color('green', callback_query.from_user.id)
        await (mental_rate_strike(callback_query.from_user.id))
        collection_name['users'].find().close()
        collection_name['mental_rate'].find().close()
    except (Exception):
        await bot.send_message(callback_query.from_user.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори отправку настроения через несколько минут или напиши разработчикам через команду /feedback")


@dp.callback_query_handler(lambda c: c.data == 'yellow_button_answer')
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)
    await get_options_color('yellow', callback_query.from_user.id)
    try:
        collection_name = get_database()
        user = collection_name["users"].find_one(
            {"telegram_id": str(callback_query.message.chat.id)}, {'_id': 1, 'name': 0})
        collection_name['mental_rate'].find_one_and_update({"$and": [{"id_user": user["_id"]}, {
                                                           "id_tg_message": callback_query.message.message_id}]}, {"$set": {"rate": 3}})
        collection_name['users'].find().close()
        collection_name['mental_rate'].find().close()
    except (Exception):
        await bot.send_message(callback_query.from_user.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори отправку настроения через несколько минут или напиши разработчикам через команду /feedback")
    await (mental_rate_strike(callback_query.from_user.id))


@dp.callback_query_handler(lambda c: c.data == 'orange_button_answer')
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)
    await get_options_color('orange', callback_query.from_user.id)
    try:
        collection_name = get_database()
        user = collection_name["users"].find_one(
            {"telegram_id": str(callback_query.message.chat.id)}, {'_id': 1, 'name': 0})
        collection_name['mental_rate'].find_one_and_update({"$and": [{"id_user": user["_id"]}, {
                                                           "id_tg_message": callback_query.message.message_id}]}, {"$set": {"rate": 2}})
        collection_name['users'].find().close()
        collection_name['mental_rate'].find().close()
    except (Exception):
        await bot.send_message(callback_query.from_user.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори отправку настроения через несколько минут или напиши разработчикам через команду /feedback")
    await (mental_rate_strike(callback_query.from_user.id))


@dp.callback_query_handler(lambda c: c.data == 'red_button_answer')
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)
    await get_options_color('red', callback_query.from_user.id)
    try:
        collection_name = get_database()
        user = collection_name["users"].find_one(
            {"telegram_id": str(callback_query.message.chat.id)}, {'_id': 1, 'name': 0})
        collection_name['mental_rate'].find_one_and_update({"$and": [{"id_user": user["_id"]}, {
                                                           "id_tg_message": callback_query.message.message_id}]}, {"$set": {"rate": 1}})
        collection_name['users'].find().close()
        collection_name['mental_rate'].find().close()
    except (Exception):
        await bot.send_message(callback_query.from_user.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори отправку настроения через несколько минут или напиши разработчикам через команду /feedback")
    await (mental_rate_strike(callback_query.from_user.id))


@dp.message_handler(commands=['version'])
async def process_version_command(message: types.Message):
    await bot.send_message(message.chat.id, "Версия бота Роджер: 0.3.3")


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    collection_name = get_database()
    user = collection_name["users"].find_one(
        {"telegram_id": str(message.chat.id)}, {'_id': 1, 'name': 1})
    if (user != None):
        await bot.send_message(message.chat.id, "Кажется, мы уже знакомы, " + user['name'])
    else:
        await bot.send_message(message.chat.id, "Привет 👋 \n \nЯ Роджер — бот для твоей кукухи.")
        time.sleep(1)
        await bot.send_message(message.chat.id, """Каждый вечер я буду интересоваться твоим настроением. \nЯ умею распознавать 4 настроения: \n
🟢 — день был великолепен, лучше и представить нельзя
🟡 — вариант для хорошего дня, в котором были небольшие неприятности
🟠 — день мог бы быть сильно лучше, но еще не все потеряно
🔴 — день был хуже некуда, тебе срочно нужна поддержка
        """)
        time.sleep(6)
        await bot.send_message(message.chat.id, "Если ты выберешь 🟠 и 🔴 настроение, тогда и начнется самое интересное 🙃 \nЯ подберу тебе ободряющее сообщение от другого пользователя, у которого настроение было отличным — и он захотел поделиться им с тобой")
        time.sleep(5)
        await bot.send_message(message.chat.id, "И наоборот — если у тебя выдался 🟢 и 🟡 день, то ты сможешь написать свое позитивное сообщение.  \nКогда твое сообщение пройдет модерацию, я буду показывать его тем, кому это сейчас важно")
        time.sleep(5)
        await bot.send_message(message.chat.id, "Вот такая простая магия ✨")
        time.sleep(3)
        await bot.send_message(message.chat.id, "Давай познакомимся с тобой поближе! Только будь внимателен — зарегистрироваться можно только один раз 🙃")
        time.sleep(5)
        await bot.send_message(message.chat.id, "Тебя зовут " + message.from_user.first_name + "? Подтверди свое имя или введи другое", reply_markup=ask_for_name_kb)
        await Recording.Name.set()
        collection_name['users'].find().close()


@dp.callback_query_handler(lambda c: c.data == 'name_button_yes', state=Recording.Name)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)
    global user_name
    user_name = callback_query.from_user.first_name
    await bot.send_message(callback_query.from_user.id, 'Приятно познакомиться, ' + user_name + '!')
    time.sleep(1)
    await state.finish()
    await get_user_time_to_send(callback_query.from_user.id)


@dp.callback_query_handler(lambda c: c.data == 'name_button_no', state=Recording.Name)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Введи свое имя ниже')
    await Recording.AwaitForAName.set()


@dp.message_handler(state=Recording.AwaitForAName)
async def customer_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    global user_name
    user_name = message.text[:80]
    if (user_name.isalpha()):
        await bot.send_message(message.chat.id, "Приятно познакомиться, " + user_name + "!")
        await state.finish()
        await get_user_time_to_send(message.chat.id)
    else:
        await bot.send_message(message.chat.id, "Ты ошибся со вводом. Ты же не ЛСДУЗ или ЙФЯУ9? \nВведи свое имя еще раз")
        await Recording.AwaitForAName.set()


async def get_user_time_to_send(chat_id: int):
    await bot.send_message(chat_id, "Во сколько часов мне лучше интересоваться твоим настроением?", reply_markup=ask_for_time_to_send_kb)
    await Recording.AwaitForATimeToSend.set()


@dp.callback_query_handler(lambda c: c.data == 'ask_for_time_20', state=Recording.AwaitForATimeToSend)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    global user_time
    user_time = 20
    await bot.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " часов каждый день")
    await state.finish()
    await get_user_time_zone(callback_query.from_user.id)


@dp.callback_query_handler(lambda c: c.data == 'ask_for_time_21', state=Recording.AwaitForATimeToSend)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    global user_time
    user_time = 21
    await bot.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " час каждый день")
    await state.finish()
    await get_user_time_zone(callback_query.from_user.id)


@dp.callback_query_handler(lambda c: c.data == 'ask_for_time_22', state=Recording.AwaitForATimeToSend)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    global user_time
    user_time = 22
    await bot.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " часа каждый день")
    await state.finish()
    await get_user_time_zone(callback_query.from_user.id)


@dp.callback_query_handler(lambda c: c.data == 'ask_for_time_23', state=Recording.AwaitForATimeToSend)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    global user_time
    user_time = 23
    await bot.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " чаcа каждый день")
    await state.finish()
    await get_user_time_zone(callback_query.from_user.id)


async def get_user_time_zone(chat_id: int):
    await bot.send_message(chat_id, "Еще мне нужно знать твой часовой пояс, чтобы присылать сообщения, когда тебе удобно \nНапиши, сколько у тебя сейчас времени в формате ЧАСЫ:МИНУТЫ")
    await Recording.AwaitForATimeZoneToSend.set()


@dp.message_handler(state=Recording.AwaitForATimeZoneToSend)
async def customer_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    user_current_time = message.text
    s = user_current_time.split(":")
    if (s[0].isdigit() == False):
        await bot.send_message(message.chat.id, "Кажется, ты ввел что-то не то 🙃 \nНапиши, сколько у тебя сейчас времени в формате ЧАСЫ:МИНУТЫ")
        await Recording.AwaitForATimeZoneToSend.set()
        return
    if (int(s[0]) < 0 or int(s[0]) > 23):
        await bot.send_message(message.chat.id, "Кажется, ты ввел что-то не то 🙃 \nНапиши, сколько у тебя сейчас времени в формате ЧАСЫ:МИНУТЫ")
        await Recording.AwaitForATimeZoneToSend.set()
        return
    time_now_utc = datetime.datetime.now(datetime.timezone.utc)
    time_zone1 = int(s[0])-time_now_utc.hour
    time_zone2 = time_now_utc.hour-int(s[0])
    if (time_zone1 < 0):
        time_zone1 = time_zone1+24
    if (abs(time_zone1) <= abs(time_zone2) and time_zone1 < 10):
        time_zone = "+0" + str(abs(time_zone1))
    elif (abs(time_zone1) <= abs(time_zone2) and time_zone1 >= 10):
        time_zone = "+" + str(abs(time_zone1))
    elif (abs(time_zone1) > abs(time_zone2) and time_zone2 < 10):
        time_zone = "-0" + str(abs(time_zone2))
    else:
        time_zone = "-" + str(abs(time_zone2))
    s = message.from_user.username
    if (s == None):
        s = ""
    await create_new_user(s, user_name, time_zone, str(message.chat.id), user_time)
    await state.finish()


async def create_new_user(tg_username: str, username: str, time_zone: str, telegram_id: str, user_time: str):
    try:
        collection_name = get_database()
        form_id = ObjectId()
        collection_name['users'].insert_one({"telegram_username": "@" + tg_username, "name": username, "timezone": time_zone, "is_volunteer": False, "is_banned_from_volunteering": False,
                                            "form_id": form_id, "telegram_id": telegram_id, "is_admin": False, "is_active": True, "created_at": datetime.datetime.now(), "time_to_send_messages": user_time})
        await bot.send_message(int(telegram_id), "Отлично! 😍")
        collection_name['users'].find().close()
        await create_new_message_after_registration(username, telegram_id, form_id)
    except (Exception):
        await bot.send_message(int(telegram_id), "Ой, кажется, что-то пошло не так 😞 \nПовтори регистрацию командой /start через несколько минут или напиши разработчикам через команду /feedback")


async def create_new_message_after_registration(name: str, telegram_id: str, form_id: ObjectId):
    await bot.send_message(int(telegram_id), user_name + ", давай создадим твое первое сообщение для тех, у кого был плохой день. \n\nНажимай на ссылку ниже — по ней откроется небольшая форма. Помни, что твое сообщение прочитает человек, которому нужна максимальная поддержка 🙌\n\n" + link_to_form + str(form_id))
    return


async def get_options(array: str):
    arr = []
    for item in texts.get(array):
        arr.append(item)
    s = await rand_select_obj_texts(arr)
    return s.get('text')


async def get_options_color(color: str, chat_id: int):
    arr = []
    for item in texts.get("polls_answers"):
        if (item.get("color") == color):
            arr.append(item)
    await get_texts_to_send_mood(await rand_select_obj_texts(arr), chat_id)


async def rand_select_obj_texts(arr: list):
    rand_id_array = []
    j = 0
    for item in arr:
        for i in range(item.get("frequency")):
            rand_id_array.append(j)
        j += 1
    return arr[rand_id_array[random.randint(0, len(rand_id_array) - 1)]]


async def get_texts_to_send_mood(arr: list, chat_id: int):
    for item in arr.get("answers_arrays"):
        collection_name = get_database()
        if (item[0] == '*' and arr.get("is_labelled") == 1):
            if item == '*gif*':
                await bot.send_video(chat_id, await get_cat_gif())
            if item == '*support*':
                arr = []
                user_id = collection_name["users"].find_one(
                    {"telegram_id": str(chat_id)}, {'_id': 1, 'name': 1})
                user_messages = collection_name["user_messages"].find(
                    {"id_user": ObjectId(str(user_id["_id"]))}, {'_id': 0, 'id_message': 1})
                for item in user_messages:
                    arr.append(ObjectId(item['id_message']))
                messages = collection_name["messages"].find_one({"$and": [{'is_approved': True}, {'id_user': {'$ne': user_id["_id"]}}, {
                                                                '_id': {"$nin": arr}}]}, {'_id': 1, 'text': 1, 'media_link': 1, 'id_user': 1, 'is_anonymous': 1, 'image_ids': 1})
                if messages != None:
                    user_who_create_message = collection_name["users"].find_one(
                        {"_id": ObjectId(str(messages['id_user']))}, {'name': 1})
                    await create_message_with_support(chat_id, messages, user_who_create_message['name'], user_id["_id"])
                else:
                    await bot.send_message(chat_id, "Извини, сообщения на сегодня закончились 😞 \nВот видео от меня, оно точно поможет:")
                    await bot.send_video(chat_id, await get_video_when_no_messages())
            if item == '*waiting_day_feedback*':
                i = 0
                # поставить вызов функции
            if item == "*wait_for_answer_to_form*":
                user_id = collection_name["users"].find_one(
                    {"telegram_id": str(chat_id)})
                await bot.send_message(chat_id, link_to_form + str(user_id['form_id']), disable_web_page_preview=True)
        else:
            s = await rand_select_obj_texts(texts.get(item))
            await bot.send_message(chat_id, s.get('text'))
            time.sleep(1)
    collection_name['users'].find().close()
    collection_name['user_messages'].find().close()
    collection_name['messages'].find().close()


async def get_cat_gif():
    response = requests.get(contentful_api_readonly_url + 'spaces/' + contenful_space_id +
                            '/environments/master/assets?access_token=' + contenful_access_token + '&metadata.tags.sys.id[all]=catGifs')
    answer = json.loads(response.content)
    answer = answer.get("items")
    answer = answer[random.randint(0, len(answer) - 1)]
    answer = answer.get("fields").get("file").get("url")
    gif_link = str(answer[2:])
    return gif_link


async def get_video_when_no_messages():
    response = requests.get(contentful_api_readonly_url + 'spaces/' + contenful_space_id + '/environments/master/assets?access_token=' +
                            contenful_access_token + '&metadata.tags.sys.id[all]=videoToSendWhenNoMessages')
    answer = json.loads(response.content)
    answer = answer.get("items")
    answer = answer[random.randint(0, len(answer) - 1)]
    answer = answer.get("fields").get("file").get("url")
    video_link = str(answer[2:])
    return video_link


async def get_pictures(picture_id: str):
    response = requests.get(contentful_api_readonly_url + 'spaces/' + contenful_space_id +
                            '/environments/master/assets/' + picture_id + '?access_token=' + contenful_access_token)
    answer = json.loads(response.content)
    answer = answer.get("fields").get("file").get("url")

    return str(answer[2:])


async def create_message_with_support(chat_id: int, cursor: list, username: str, user_to_send: ObjectId):
    if cursor['is_anonymous'] == True:
        message = text(bold("Имя: ") + "Аноним" + '\n')
    else:
        message = text(bold("Имя: ") + username + '\n')
    if len(cursor['image_ids']) > 0:
        message = message + '\n' + text(bold('Вложения:'))
        await bot.send_message(chat_id, message, parse_mode=ParseMode.MARKDOWN)
        message = ""
        media = types.MediaGroup()
        for i in cursor['image_ids']:
            picture_url = await get_pictures(i)
            if ('.gif' in picture_url):
                # Пробовал attach_video тут, но почему-то крашится
                media.attach_photo(picture_url)
            else:
                media.attach_photo(picture_url + '?fm=jpg')
        await bot.send_media_group(chat_id, media=media)
    else:
        message = message + '\n'
    message = message + text(bold("Сообщение: ") +
                             '\n' + cursor['text'] + '\n')
    message = message + '\n'
    if cursor['media_link'] != "":
        message = message + \
            text(bold("Что стоит глянуть: ") + '\n' + cursor['media_link'])
    try:
        collection_name = get_database()
        user = collection_name["users"].find_one(
            {"telegram_id": str(chat_id)}, {'_id': 1})
        id_previous_mes = collection_name['user_messages'].find_one({"id_user": user['_id']}, {
                                                                    "id_user": 1, "id_message": 1, "id_tg_message": 1}, sort=[("time_to_send", -1)])
        if (id_previous_mes != None):
            rate_previous_mes = collection_name['rate'].find_one(
                {"id_message": id_previous_mes['id_message'], 'id_user': id_previous_mes['id_user']})
            if (rate_previous_mes == None):
                await delete_keyboard(chat_id, id_previous_mes['id_tg_message'])
        id_message = await bot.send_message(chat_id, message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True, reply_markup=ask_for_rate_messages)
        collection_name['user_messages'].insert_one({"id_user": user_to_send, "id_message": cursor["_id"], "time_to_send": datetime.datetime.now(
        ), "id_tg_message": id_message.message_id})
        collection_name['user_messages'].find().close()
    except (Exception):
        await bot.send_message(chat_id, "Ой, кажется, что-то пошло не так 😞 \nПовтори действие через несколько минут или напиши разработчикам через команду /feedback")


@dp.callback_query_handler(lambda c: c.data == 'rate_good')
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    try:
        collection_name = get_database()
        message_to_update = collection_name['user_messages'].find_one(
            {"id_tg_message": callback_query.message.message_id}, {"_id": 0, "id_message": 1, "id_user": 1})
        collection_name['rate'].insert_one({"id_user": message_to_update["id_user"],
                                           "id_message": message_to_update["id_message"], "rate": True, "created_at": datetime.datetime.now()})
        collection_name['rate'].find().close()
        collection_name['user_messages'].find().close()
        await bot.send_message(callback_query.from_user.id, "Спасибо за оценку! Продолжайте наблюдение 😎")
    except (Exception):
        await bot.send_message(callback_query.from_user.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори действие через несколько минут или напиши разработчикам через команду /feedback")


@dp.callback_query_handler(lambda c: c.data == 'rate_bad')
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    try:
        collection_name = get_database()
        message_to_update = collection_name['user_messages'].find_one(
            {"id_tg_message": callback_query.message.message_id}, {"_id": 0, "id_message": 1, "id_user": 1})
        collection_name['rate'].insert_one({"id_user": message_to_update["id_user"],
                                           "id_message": message_to_update["id_message"], "rate": False, "created_at": datetime.datetime.now()})
        collection_name['rate'].find().close()
        collection_name['user_messages'].find().close()
        await bot.send_message(callback_query.from_user.id, "Спасибо за оценку! Продолжайте наблюдение 😎")
    except (Exception):
        await bot.send_message(callback_query.from_user.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори действие через несколько минут или напиши разработчикам через команду /feedback")


async def is_enabled():
    while True:
        s = datetime.datetime.now().strftime("%H")
        collection_name = get_database()
        users = collection_name["users"].aggregate([
            {
                '$match': {
                    'is_active': True
                }
            }, {
                '$addFields': {
                    'current_time': {
                        '$toDouble': {
                            '$dateToString': {
                                'date': datetime.datetime.now(pytz.utc),
                                'format': '%H'
                            }
                        }
                    }
                }
            }, {
                '$addFields': {
                    'user_time': {
                        '$toDouble': '$timezone'
                    }
                }
            }, {
                '$addFields': {
                    'current_user_time': {
                        '$add': [
                            '$user_time', '$current_time'
                        ]
                    }
                }
            }, {
                '$addFields': {
                    'result': {
                        '$lte': [
                            '$time_to_send_messages', '$current_user_time'
                        ]
                    }
                }
            }, {
                '$match': {
                    'result': True
                }
            }
        ])
        for user in users:
            already_sent = await is_any_messages_sent_today(user['_id'])
            if (not already_sent):
                await sendmes(int(user['telegram_id']))
        collection_name['users'].find().close()
        collection_name['user_messages'].find().close()
        await asyncio.sleep(45*60)


async def sendmes(chat_id: int):
    try:
        collection_name = get_database()
        user = collection_name["users"].find_one(
            {"telegram_id": str(chat_id)}, {'_id': 1, 'id_user': 1})
        id_previous_mes = collection_name['mental_rate'].find_one(
            {"rate": 0, "id_user": user['_id']}, {'id_tg_message': 1}, sort=[("date", -1)])
        if (id_previous_mes != None):
            await delete_keyboard(chat_id, id_previous_mes['id_tg_message'])
        id = await bot.send_message(chat_id, await get_options('polls_questions'), parse_mode=ParseMode.MARKDOWN, reply_markup=kb_for_mental_poll)
        collection_name['mental_rate'].insert_one(
            {"rate": 0, "id_user": user['_id'], "date": datetime.datetime.now(), "id_tg_message": id.message_id})
        collection_name['users'].find().close()
        collection_name['mental_rate'].find().close()
    except (Exception):
        await bot.send_message(chat_id, "Ой, кажется, что-то пошло не так 😞 \nПовтори отправку настроения через несколько минут или напиши разработчикам через команду /feedback")


async def on_startup(x):
    asyncio.create_task(is_enabled())


async def mental_rate_strike(chat_id: int):
    collection_name = get_database()
    user = collection_name["users"].find_one(
        {"telegram_id": str(chat_id)}, {'_id': 1})
    all_rates = collection_name['mental_rate'].find(
        {"$and": [{"id_user": user["_id"]}, {"rate": {"$gt": 0}}]}, sort=[("date", -1)])
    if (len(list(all_rates.clone())) == 7):
        await ask_to_be_a_volunteer(chat_id)
    collection_name['users'].find().close()
    collection_name['mental_rate'].find().close()


async def ask_to_be_a_volunteer(chat_id: int):
    await bot.send_message(chat_id, "Ты дружишь со мной уже давно! Как насчет помочь мне с оценкой сообщений пользователей? \n\n Переходи в бота для волонтеров @JimmyVolunteerBot и нажимай /start")
    collection_name = get_database()
    collection_name['users'].find_one_and_update({"telegram_id": str(chat_id)}, {
                                                 "$set": {"is_volunteer": True}})
    collection_name['users'].find().close()


@dp.message_handler(commands=['sendmestoall'])
async def process_feedback_command(message: types.Message):
    await Recording.AwaitForAMessageForAll.set()
    await bot.send_message(message.chat.id, "Отправь любое сообщение (текст или фото) — и я перешлю его всем пользователям")


@dp.message_handler(state=Recording.AwaitForAMessageForAll)
async def process_callback_button1(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    collection_name = get_database()
    user = collection_name["users"].find_one({"telegram_id": str(message.chat.id)}, {
                                             '_id': 1, "form_id": 1, "is_admin": 1})
    if (user["is_admin"] == False):
        await bot.send_message(message.chat.id, "Сорри, ты не админ этого бота. Не расстраивайся, ты же клиент!")
        await state.finish()
        return
    users = collection_name["users"].find(
        {"is_active": True}, {'_id': 1, "telegram_id": 1, "is_admin": 1})
    for i in users:
        await bot.send_message(i["telegram_id"], message.text)
    await state.finish()
    collection_name['users'].find().close()


async def is_any_messages_sent_today(user_id: ObjectId):
    collection_name = get_database()
    mental_rates = collection_name['mental_rate'].aggregate(
        [
            {
                '$match': {
                    'id_user': user_id
                }
            }, {
                '$addFields': {
                    'current_date': {
                        '$dateToParts': {
                            'date': datetime.datetime.now(pytz.utc)
                        }
                    }
                }
            }, {
                '$addFields': {
                    'current_date': {
                        '$dateFromParts': {
                            'year': '$current_date.year',
                            'month': '$current_date.month',
                            'day': '$current_date.day'
                        }
                    }
                }
            }, {
                '$addFields': {
                    'dateComp': {
                        '$cmp': [
                            '$current_date', '$date'
                        ]
                    }
                }
            }, {
                '$match': {
                    'dateComp': -1
                }
            }
        ]
    )

    result = (list(mental_rates) != [])
    collection_name['mental_rate'].find().close()
    return result

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
