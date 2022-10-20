import asyncio
from curses.ascii import isdigit
from reprlib import aRepr
from sqlite3 import Cursor
from config import token_bot, db_token, link_to_form, contenful_access_token, contenful_space_id, contentful_api_readonly_url
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import requests
import json
import random
import time
import datetime
from aiogram import Bot, types
from aiogram.utils.markdown import hbold, bold, text, link
from aiogram.types import ChatType, ParseMode, ContentTypes
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton 
from states import Recording
import json
from pymongo import MongoClient
from bson import ObjectId

global user_name
global user_time
global time_zone

with open('texts.json') as t:
    texts = json.load(t)

green_button_answer=InlineKeyboardButton('🟢', callback_data='green_button_answer')
yellow_button_answer=InlineKeyboardButton('🟡', callback_data='yellow_button_answer')
orange_button_answer=InlineKeyboardButton('🟠', callback_data='orange_button_answer')
red_button_answer=InlineKeyboardButton('🔴', callback_data='red_button_answer')
kb_for_mental_poll=InlineKeyboardMarkup(row_width=4).add(green_button_answer, yellow_button_answer, orange_button_answer, red_button_answer)

ask_for_name_yes = InlineKeyboardButton('Это мое имя', callback_data='name_button_yes')
ask_for_name_no = InlineKeyboardButton('Задать другое имя', callback_data='name_button_no')
ask_for_name_kb = InlineKeyboardMarkup().add(ask_for_name_yes, ask_for_name_no)

ask_for_time_to_send_20 = InlineKeyboardButton('20:00-21:00', callback_data='ask_for_time_20')
ask_for_time_to_send_21 = InlineKeyboardButton('21:00-22:00', callback_data='ask_for_time_21')
ask_for_time_to_send_22 = InlineKeyboardButton('22:00-23:00', callback_data='ask_for_time_22')
ask_for_time_to_send_23 = InlineKeyboardButton('23:00-00:00', callback_data='ask_for_time_23')
ask_for_time_to_send_kb = InlineKeyboardMarkup(row_width=2).add(ask_for_time_to_send_20, ask_for_time_to_send_21, ask_for_time_to_send_22, ask_for_time_to_send_23)

bot = Bot(token=token_bot)
dp = Dispatcher(bot, storage=MemoryStorage())

def get_database():
    client = MongoClient(db_token)
    collection_name = client["roger-bot-db"]
    return collection_name

@dp.message_handler(commands=['reg'])
async def process_start_command(message: types.Message):

    #collection_name['users'].insert_one({"name": "test"})
    return

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await bot.send_message(message.chat.id, await get_options('polls_questions'), parse_mode=ParseMode.MARKDOWN, reply_markup=kb_for_mental_poll)

@dp.callback_query_handler(lambda c: c.data == 'green_button_answer')
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)
    await get_options_color('green', callback_query.from_user.id)    
    #записать в базу выбранный вариант
    return

async def delete_keyboard (chat_id: int, message_id: int):
    await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
    return

@dp.callback_query_handler(lambda c: c.data == 'yellow_button_answer')
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)
    await get_options_color('yellow', callback_query.from_user.id)    
    #записать в базу выбранный вариант
    return

@dp.callback_query_handler(lambda c: c.data == 'orange_button_answer')
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)
    await get_options_color('orange', callback_query.from_user.id)    
        #записать в базу выбранный вариант
    return

@dp.callback_query_handler(lambda c: c.data == 'red_button_answer')
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)
    await get_options_color('red', callback_query.from_user.id)
        #записать в базу выбранный вариант
    return

@dp.message_handler(commands=['meet'])
async def process_start_command(message: types.Message):
    collection_name = get_database()
    user = collection_name["users"].find_one({"telegram_id" : str(message.chat.id)}, {'_id': 1, 'name': 1})
    if (user==None):
        await bot.send_message(message.chat.id, "Кажется, мы уже знакомы. Ты же " + user['name'] + ", верно?")
    else: 
        await bot.send_message(message.chat.id, "Привет 👋 \n \nЯ Роджер — бот для твоей кукухи.")
        time.sleep(1)
        await bot.send_message(message.chat.id, """Каждый вечер я буду интересоваться твоим настроением. \nЯ умею распознавать 4 настроения: \n
🟢 — день был великолепен, лучше и представить нельзя
🟡 — вариант для хорошего дня, в котором были небольшие неприятности
🟠 — день мог бы быть сильно лучше, но еще не все потеряно
🔴 — день был хуже некуда, тебе срочно нужна поддержка
        """)
        time.sleep(4)
        await bot.send_message(message.chat.id, "Если ты выберешь 🟠 и 🔴 настроение, тогда и начнется самое интересное 🙃 \nЯ подберу тебе ободряющее сообщение от другого пользователя, у которого настроение было отличным — и он захотел поделиться им с тобой")
        time.sleep(3)
        await bot.send_message(message.chat.id, "И наоборот — если у тебя выдался 🟢 и 🟡 день, то ты сможешь написать свое позитивное сообщение")
        time.sleep(2)
        await bot.send_message(message.chat.id, "Когда твое сообщение пройдет модерацию, я буду показывать его тем, кому это сейчас важно")
        time.sleep(2)
        await bot.send_message(message.chat.id, "Вот такая простая магия ✨")
        time.sleep(2)
        await bot.send_message(message.chat.id, "Давай познакомимся с тобой поближе! Только будь внимателен — зарегистрироваться можно только один раз 🙃")
        time.sleep(2)
        await bot.send_message(message.chat.id, "Тебя зовут " + message.from_user.first_name + "? Подтверди свое имя или введи другое", reply_markup=ask_for_name_kb)         
        await Recording.Name.set()
    return     

@dp.callback_query_handler(lambda c: c.data == 'name_button_yes', state=Recording.Name)
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await bot.answer_callback_query(callback_query.id)
    user_name=callback_query.from_user.first_name
    await bot.send_message(callback_query.from_user.id, 'Приятно познакомиться, ' + user_name + '!') 
    time.sleep(1)
    await state.finish()

    return

@dp.callback_query_handler(lambda c: c.data == 'name_button_no', state=Recording.Name)
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Введи свое имя ниже')  
    await Recording.AwaitForAName.set()
    return

@dp.message_handler(state=Recording.AwaitForAName)
async def customer_name(message: types.Message, state:FSMContext):
    await state.update_data(name=message.text)
    user_name=message.text
    if (user_name.isalpha()):
        await bot.send_message(message.chat.id, "Приятно познакомиться, " + user_name + "!")
        await state.finish()
    else:
        await bot.send_message(message.chat.id, "Ты ошибся со вводом. Ты же не ЛСДУЗ или ЙФЯУ9? \nВведи свое имя еще раз")
        await Recording.AwaitForAName.set()
    return

@dp.message_handler(commands=['time'])
async def process_start_command(message: types.Message):
    await bot.send_message(message.chat.id, "Во сколько часов мне лучше интересоваться твоим настроением?", reply_markup=ask_for_time_to_send_kb)
    await Recording.AwaitForATimeToSend.set()
    return 

@dp.callback_query_handler(lambda c: c.data == 'ask_for_time_20', state=Recording.AwaitForATimeToSend)
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    user_time = 20
    await bot.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " часов каждый день")
    await state.finish()
    return

@dp.callback_query_handler(lambda c: c.data == 'ask_for_time_21', state=Recording.AwaitForATimeToSend)
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    user_time = 21
    await bot.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " час каждый день")
    await state.finish()
    return

@dp.callback_query_handler(lambda c: c.data == 'ask_for_time_22', state=Recording.AwaitForATimeToSend)
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    user_time = 22
    await bot.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " часа каждый день")
    await state.finish()
    return 

@dp.callback_query_handler(lambda c: c.data == 'ask_for_time_23', state=Recording.AwaitForATimeToSend)
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    user_time = 23
    await bot.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " чаcа каждый день")
    await state.finish()
    return

@dp.message_handler(commands=['timezone'])
async def process_start_command(message: types.Message):
    await bot.send_message(message.chat.id, "Остался последний шаг — мне нужно знать твой часовой пояс, чтобы присылать сообщения вовремя \nНапиши, сколько у тебя сейчас времени в формате ЧАСЫ:МИНУТЫ")
    await Recording.AwaitForATimeZoneToSend.set()
    return 

@dp.message_handler(state=Recording.AwaitForATimeZoneToSend)
async def customer_name(message: types.Message, state:FSMContext):
    await state.update_data(name=message.text)
    user_current_time=message.text
    s = user_current_time.split(":")
    if (s[0].isdigit() == False):
        await bot.send_message(message.chat.id, "Кажется, ты ввел что-то не то 🙃 \nНапиши, сколько у тебя сейчас времени в формате ЧАСЫ:МИНУТЫ")
        await Recording.AwaitForATimeZoneToSend.set()
        return
    if (int(s[0])<0 or int(s[0])>24):
        await bot.send_message(message.chat.id, "Кажется, ты ввел что-то не то 🙃 \nНапиши, сколько у тебя сейчас времени в формате ЧАСЫ:МИНУТЫ")
        await Recording.AwaitForATimeZoneToSend.set()
        return
    time_now_utc = datetime.datetime.now(datetime.timezone.utc)
    time_zone1 = int(s[0])-time_now_utc.hour
    time_zone2 = time_now_utc.hour-int(s[0])
    if (time_zone1<0):
        time_zone1 = time_zone1+24
    if (abs(time_zone1)<=abs(time_zone2)):
        time_zone = "UTC+" + str(abs(time_zone1))
    else: 
        time_zone = "UTC-" + str(time_zone2) 
    await create_new_user ()
    await state.finish()
    return

async def create_new_user():
    #collection_name['users'].insert_one({"name": "test"})
    return

async def is_enabled():
    users = [71488343, 408662782]
    while True:
        for user_id in users:
              await bot.send_message(user_id, await get_options('polls_questions'), parse_mode=ParseMode.MARKDOWN, reply_markup=kb_for_mental_poll)
              await asyncio.sleep(24*60*60)

async def on_startup(x):
    asyncio.create_task(is_enabled())

async def get_options (array: str):
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
        j+=1 
    return arr[rand_id_array[random.randint(0, len(rand_id_array) - 1)]]

async def get_texts_to_send_mood(arr: list, chat_id: int):
    for item in arr.get("answers_arrays"):
        collection_name = get_database()
        if (item[0] == '*' and arr.get("is_labelled") == 1):
            if item == '*gif*':
                await bot.send_video(chat_id, await get_cat_gif())
            if item == '*support*':
                arr = []
                user_id = collection_name["users"].find({"telegram_id" : str(chat_id)}, {'_id': 1, 'name': 1})
                user_messages = collection_name["user_messages"].find({"id_user": ObjectId(str(user_id[0]["_id"]))}, {'_id': 0, 'id_message': 1})
                for item in user_messages:
                    arr.append(ObjectId(item['id_message']))
                messages = collection_name["messages"].find({"$and": [{'is_approved' : True}, {'id_user' : {'$ne': user_id[0]}}, {'_id': {"$nin": arr}}]}, {'_id': 0, 'text': 1, 'media_link': 1, 'id_user': 1, 'is_anonymous': 1, 'image_ids': 1})
                if len(list(messages.clone()))>0:
                    user_who_create_message = collection_name["users"].find({"_id" : ObjectId(str(messages[0]['id_user']))}, {'name': 1})
                    await create_message_with_support (chat_id, messages, user_who_create_message[0]['name'])       
            if item == '*waiting_day_feedback*':
                i=0
                #поставить вызов функции
            if item == "*wait_for_answer_to_form*":
                user_id = collection_name["users"].find({"telegram_id" : str(chat_id)})
                await bot.send_message(chat_id, link_to_form + str(user_id[0]['form_id']), disable_web_page_preview=True)
        else:
            s = await rand_select_obj_texts(texts.get(item))
            await bot.send_message(chat_id, s.get('text'))
            time.sleep(1)
    return

async def get_cat_gif ():
    response = requests.get(contentful_api_readonly_url + 'spaces/' + contenful_space_id + '/environments/master/assets?access_token=' + contenful_access_token + '&metadata.tags.sys.id[all]=catGifs')
    answer = json.loads (response.content)
    answer = answer.get("items")
    answer = answer[random.randint(0, len(answer) - 1)]
    answer = answer.get("fields").get("file").get("url")
    gif_link = str(answer[2:])
    return gif_link

async def get_pictures (picture_id: str):
    response = requests.get(contentful_api_readonly_url + 'spaces/' + contenful_space_id + '/environments/master/assets/' + picture_id +'?access_token=' + contenful_access_token)
    answer = json.loads (response.content)
    answer = answer.get("fields").get("file").get("url")
    return str(answer[2:])

async def create_message_with_support (chat_id: int, cursor: Cursor, user_name: str):
    if cursor[0]['is_anonymous'] == True: 
        message = text(bold("Имя: ") + "Аноним" + '\n')  
    else: 
        message = text(bold("Имя: ") + user_name + '\n') 
    message = message + '\n'
    message = message + text(bold("Сообщение: ") + '\n' + cursor[0]['text'] + '\n')
    message = message + '\n'
    if cursor[0]['media_link']!= "":
        message = message + text(bold("Что стоит глянуть: ") + '\n' + cursor[0]['media_link'])
    await bot.send_message(chat_id, message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    if len(cursor[0]['image_ids'])>0:
        media = types.MediaGroup()
        for i in cursor[0]['image_ids']:
            media.attach_photo(await get_pictures(i))
        await bot.send_media_group(chat_id, media=media)
        #записать в базу отправленное сообщение

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)