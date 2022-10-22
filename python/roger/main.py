from curses.ascii import isdigit
from sqlite3 import Cursor
import json
import random
import time
import os

import asyncio
import requests
import datetime
import certifi
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, types
from aiogram.utils.markdown import hbold, bold, text, link
from aiogram.types import ChatType, ParseMode, ContentTypes
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from bson import ObjectId

from states import Recording
from keyboards import kb_for_mental_poll, ask_for_name_kb, ask_for_rate_messages, ask_for_time_to_send_kb

token_bot = os.getenv("TOKEN_BOT")
db_token = os.getenv("MONGODB_URI")
link_to_form = os.getenv("LINK_TO_FORM")
contenful_access_token = os.getenv("CONTENTFUL_ACCESS_TOKEN")
contenful_space_id = os.getenv("CONTENTFUL_SPACE_ID")
contentful_api_readonly_url = os.getenv("CONTENTFUL_API_READONLY_URL")

with open('texts.json') as t:
    texts = json.load(t)

bot = Bot(token=token_bot)
dp = Dispatcher(bot, storage=MemoryStorage())

def get_database():
    client = MongoClient(db_token)
    collection_name = client["roger-bot-db"]
    return collection_name

@dp.message_handler(commands=['feedback'])
async def process_start_command(message: types.Message):
     await Recording.AwaitForAFeedback.set()    

@dp.message_handler(commands=['sendmes'])
async def process_start_command(message: types.Message):
    await bot.send_message(message.chat.id, await get_options('polls_questions'), parse_mode=ParseMode.MARKDOWN, reply_markup=kb_for_mental_poll)
    try:
        collection_name = get_database()
        user = collection_name["users"].find_one({"telegram_id" : str(message.chat.id)}, {'_id': 1, 'name': 0})
        collection_name['mental_rate'].insert_one({"rate": 0, "id_user": user['_id'], "date": datetime.datetime.now(), "id_tg_message": message.message_id})
        collection_name['users'].find().close()
        collection_name['mental_rate'].find().close()
    except(Exception):
        await bot.send_message(message.chat.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори отправку настроения через несколько минут или напиши разработчикам через команду /feedback")

@dp.callback_query_handler(lambda c: c.data == 'green_button_answer')
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)
    try:
        collection_name = get_database()
        user = collection_name["users"].find_one({"telegram_id" : str(callback_query.message.chat.id)}, {'_id': 1, 'name': 0})
        collection_name['mental_rate'].insert_one({"rate": 4, "id_user": user['_id'], "date": datetime.datetime.now() })
        collection_name['users'].find().close()
        collection_name['mental_rate'].find().close()
    except(Exception):
        await bot.send_message(callback_query.from_user.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори отправку настроения через несколько минут или напиши разработчикам через команду /feedback")
    await get_options_color('green', callback_query.from_user.id)    
    

async def delete_keyboard (chat_id: int, message_id: int):
    await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
    

@dp.callback_query_handler(lambda c: c.data == 'yellow_button_answer')
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)
    await get_options_color('yellow', callback_query.from_user.id)    
    try:
        collection_name = get_database()
        user = collection_name["users"].find_one({"telegram_id" : str(callback_query.message.chat.id)}, {'_id': 1, 'name': 0})
        collection_name['mental_rate'].insert_one({"rate": 3, "id_user": user['_id'], "date": datetime.datetime.now() })
        collection_name['users'].find().close()
        collection_name['mental_rate'].find().close()
    except(Exception):
        await bot.send_message(callback_query.from_user.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори отправку настроения через несколько минут или напиши разработчикам через команду /feedback")
    

@dp.callback_query_handler(lambda c: c.data == 'orange_button_answer')
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)
    await get_options_color('orange', callback_query.from_user.id)    
    try:
        collection_name = get_database()
        user = collection_name["users"].find_one({"telegram_id" : str(callback_query.message.chat.id)}, {'_id': 1, 'name': 0})
        collection_name['mental_rate'].insert_one({"rate": 2, "id_user": user['_id'], "date": datetime.datetime.now() })
        collection_name['users'].find().close()
        collection_name['mental_rate'].find().close()
    except(Exception):
        await bot.send_message(callback_query.from_user.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори отправку настроения через несколько минут или напиши разработчикам через команду /feedback")
    

@dp.callback_query_handler(lambda c: c.data == 'red_button_answer')
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)
    await get_options_color('red', callback_query.from_user.id)
    try:
        collection_name = get_database()
        user = collection_name["users"].find_one({"telegram_id" : str(callback_query.message.chat.id)}, {'_id': 1, 'name': 0})
        collection_name['mental_rate'].insert_one({"rate": 1, "id_user": user['_id'], "date": datetime.datetime.now()})
        collection_name['users'].find().close()
        collection_name['mental_rate'].find().close()
    except(Exception):
        await bot.send_message(callback_query.from_user.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори отправку настроения через несколько минут или напиши разработчикам через команду /feedback")
    

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    collection_name = get_database()
    user = collection_name["users"].find_one({"telegram_id" : str(message.chat.id)}, {'_id': 1, 'name': 1})
    if (user!=None):
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
        await bot.send_message(message.chat.id, "И наоборот — если у тебя выдался 🟢 и 🟡 день, то ты сможешь написать свое позитивное сообщение  \nКогда твое сообщение пройдет модерацию, я буду показывать его тем, кому это сейчас важно")
        time.sleep(4)
        await bot.send_message(message.chat.id, "Вот такая простая магия ✨")
        time.sleep(2)
        await bot.send_message(message.chat.id, "Давай познакомимся с тобой поближе! Только будь внимателен — зарегистрироваться можно только один раз 🙃")
        time.sleep(2)
        await bot.send_message(message.chat.id, "Тебя зовут " + message.from_user.first_name + "? Подтверди свое имя или введи другое", reply_markup=ask_for_name_kb)         
        await Recording.Name.set()
        collection_name['users'].find().close()
         

@dp.callback_query_handler(lambda c: c.data == 'name_button_yes', state=Recording.Name)
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await bot.answer_callback_query(callback_query.id)
    global user_name
    user_name=callback_query.from_user.first_name
    await bot.send_message(callback_query.from_user.id, 'Приятно познакомиться, ' + user_name + '!') 
    time.sleep(1)
    await state.finish()
    await get_user_time_to_send(callback_query.from_user.id)
    

@dp.callback_query_handler(lambda c: c.data == 'name_button_no', state=Recording.Name)
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Введи свое имя ниже')  
    await Recording.AwaitForAName.set()
    

@dp.message_handler(state=Recording.AwaitForAName)
async def customer_name(message: types.Message, state:FSMContext):
    await state.update_data(name=message.text)
    global user_name
    user_name=message.text[:80]
    if (user_name.isalpha()):
        await bot.send_message(message.chat.id, "Приятно познакомиться, " + user_name + "!")
        await state.finish()
        await get_user_time_to_send(message.chat.id)
    else:
        await bot.send_message(message.chat.id, "Ты ошибся со вводом. Ты же не ЛСДУЗ или ЙФЯУ9? \nВведи свое имя еще раз")
        await Recording.AwaitForAName.set()
    

async def get_user_time_to_send (chat_id: int): 
    await bot.send_message(chat_id, "Во сколько часов мне лучше интересоваться твоим настроением?", reply_markup=ask_for_time_to_send_kb)
    await Recording.AwaitForATimeToSend.set()
     

@dp.callback_query_handler(lambda c: c.data == 'ask_for_time_20', state=Recording.AwaitForATimeToSend)
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    global user_time 
    user_time = 20
    await bot.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " часов каждый день")
    await state.finish()
    await get_user_time_zone(callback_query.from_user.id)
    

@dp.callback_query_handler(lambda c: c.data == 'ask_for_time_21', state=Recording.AwaitForATimeToSend)
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    global user_time 
    user_time = 21
    await bot.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " час каждый день")
    await state.finish()
    await get_user_time_zone(callback_query.from_user.id)
    

@dp.callback_query_handler(lambda c: c.data == 'ask_for_time_22', state=Recording.AwaitForATimeToSend)
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    global user_time 
    user_time = 22
    await bot.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " часа каждый день")
    await state.finish()
    await get_user_time_zone(callback_query.from_user.id)
     

@dp.callback_query_handler(lambda c: c.data == 'ask_for_time_23', state=Recording.AwaitForATimeToSend)
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    global user_time 
    user_time = 23
    await bot.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " чаcа каждый день")
    await state.finish()
    await get_user_time_zone(callback_query.from_user.id)
    

async def get_user_time_zone (chat_id: int):
    await bot.send_message(chat_id, "Остался последний шаг — мне нужно знать твой часовой пояс, чтобы присылать сообщения вовремя \nНапиши, сколько у тебя сейчас времени в формате ЧАСЫ:МИНУТЫ")
    await Recording.AwaitForATimeZoneToSend.set()
     

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
    await create_new_user(message.from_user.username, user_name, time_zone, str(message.chat.id), user_time)
    await state.finish()
    

async def create_new_user(tg_username: str, username: str, time_zone: str, telegram_id: str, user_time: str):
    try:
        collection_name = get_database()
        collection_name['users'].insert_one({"telegram_username": "@" + tg_username, "name": username, "timezone": time_zone, "is_volunteer": False, "is_banned_from_volunteering": False, "form_id": ObjectId(), "telegram_id": telegram_id, "is_admin": False, "is_active": True, "created_at": datetime.datetime.now(), "time_to_send_messages": user_time})
        await bot.send_message(int(telegram_id), "Отлично! 😍")
        collection_name['users'].find().close()
    except (Exception): 
        await bot.send_message(int(telegram_id), "Ой, кажется, что-то пошло не так 😞 \nПовтори регистрацию командой /start через несколько минут или напиши разработчикам через команду /feedback")
        

async def is_enabled():
    # collection_name = get_database()
    # users = collection_name["users"].find({"is_active": True}, {"_id": 1, "telegram_id": 1})
    # users = [71488343]
    # while True:
    #     for user_id in users:
    #           s = collection_name["user_messages"].find({"id_user": user_id["_id"]}).sort("time_to_send", -1)
    #           await bot.edit_message_reply_markup(int(user_id["telegram_id"]), s[0]["id_tg_message"], reply_markup=None)
    #           await bot.send_message(int(user_id["telegram_id"]), await get_options('polls_questions'), parse_mode=ParseMode.MARKDOWN, reply_markup=kb_for_mental_poll)
    #           await asyncio.sleep(24*60*60)
    #        collection_name['users'].find().close()
    #       collection_name['user_messages'].find().close()
    return

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
                messages = collection_name["messages"].find_one({"$and": [{'is_approved' : True}, {'id_user' : {'$ne': user_id[0]["_id"]}}, {'_id': {"$nin": arr}}]}, {'_id': 1, 'text': 1, 'media_link': 1, 'id_user': 1, 'is_anonymous': 1, 'image_ids': 1})
                if messages!=None:
                    user_who_create_message = collection_name["users"].find_one({"_id" : ObjectId(str(messages['id_user']))}, {'name': 1})
                    await create_message_with_support (chat_id, messages, user_who_create_message['name'], user_id[0]["_id"])  
                else:
                    await bot.send_message(chat_id, "Извини, сообщения на сегодня закончились 😞 \nВот видео от меня, оно точно поможет:") 
                    #вызов видео                
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
    collection_name['users'].find().close()
    collection_name['user_messages'].find().close()
    collection_name['messages'].find().close()
    

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

async def create_message_with_support (chat_id: int, cursor: list, username: str, user_to_send: ObjectId):
    if cursor['is_anonymous'] == True: 
        message = text(bold("Имя: ") + "Аноним" + '\n')  
    else: 
        message = text(bold("Имя: ") + username + '\n') 
    if len(cursor['image_ids'])>0:
        message = message + '\n' + text(bold('Вложения:'))
        await bot.send_message(chat_id, message, parse_mode=ParseMode.MARKDOWN)
        message = ""
        media = types.MediaGroup()
        for i in cursor['image_ids']:
            media.attach_photo(await get_pictures(i))
        await bot.send_media_group(chat_id, media=media)   
    else: 
        message = message + '\n'
    message = message + text(bold("Сообщение: ") + '\n' + cursor['text'] + '\n')
    message = message + '\n'
    if cursor['media_link']!= "":
        message = message + text(bold("Что стоит глянуть: ") + '\n' + cursor['media_link'])
    id_message = await bot.send_message(chat_id, message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True, reply_markup=ask_for_rate_messages)
    try: 
        collection_name = get_database()       
        collection_name['user_messages'].insert_one({"id_user": user_to_send, "id_message": cursor["_id"], "time_to_send": datetime.datetime.now(), "id_tg_message": id_message.message_id})
        collection_name['user_messages'].find().close()
    except (Exception):
        await bot.send_message(chat_id, "Ой, кажется, что-то пошло не так 😞 \nПовтори действие через несколько минут или напиши разработчикам через команду /feedback")
        

@dp.callback_query_handler(lambda c: c.data == 'rate_good')
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    try:
        collection_name = get_database()
        message_to_update = collection_name['user_messages'].find_one({"id_tg_message": callback_query.message.message_id}, {"_id": 0, "id_message": 1, "id_user": 1})
        collection_name['rate'].insert_one({"id_user": message_to_update["id_user"], "id_message": message_to_update["id_message"], "rate": True, "created_at": datetime.datetime.now()})
        collection_name['rate'].find().close()
        collection_name['user_messages'].find().close()
    except (Exception): 
        await bot.send_message(callback_query.from_user.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори действие через несколько минут или напиши разработчикам через команду /feedback")
    

@dp.callback_query_handler(lambda c: c.data == 'rate_bad')
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    try:
        collection_name = get_database()
        message_to_update = collection_name['user_messages'].find_one({"id_tg_message": callback_query.message.message_id}, {"_id": 0, "id_message": 1, "id_user": 1})
        collection_name['rate'].insert_one({"id_user": message_to_update["id_user"], "id_message": message_to_update["id_message"], "rate": False, "created_at": datetime.datetime.now()})
        collection_name['rate'].find().close()
        collection_name['user_messages'].find().close()
    except (Exception): 
        await bot.send_message(callback_query.from_user.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори действие через несколько минут или напиши разработчикам через команду /feedback")
    

if __name__ == "__main__":
    executor.start_polling(dp) #on_startup=on_startup)