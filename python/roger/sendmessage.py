from aiogram.types import ParseMode
from aiogram import types
from aiogram.utils.callback_data import CallbackData
from common import delete_keyboard, get_options
import datetime
from keyboards import kb_for_mental_poll
from database import get_database
from aiogram.dispatcher import FSMContext
from bson import ObjectId
from aiogram.utils.markdown import bold, text
from common import get_pictures
from keyboards import ask_for_rate_messages
import requests
from volunteers import mental_rate_strike, how_many_days_user_with_us
import json
import random
import time
from config import contentful_api_readonly_url, contenful_space_id, contenful_access_token, link_to_form, bot
from common import rand_select_obj_texts
from mentalstrikes import mental_rates_strike_in_a_row


cart_cb = CallbackData("q", "id", "button_parameter")

# read texts from json file
with open('texts.json') as t:
    texts = json.load(t)

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


async def callback_after_click_on_color_button(callback_query: types.CallbackQuery, state: FSMContext, rate: int, color: str):
    await bot.answer_callback_query(callback_query.id)
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    try:
        collection_name = get_database()
        user = collection_name["users"].find_one(
            {"telegram_id": str(callback_query.from_user.id)}, {'_id': 1, 'name': 0})
        collection_name['mental_rate'].find_one_and_update({"$and": [{"id_user": user["_id"]}, {
                                                           "id_tg_message": callback_query.message.message_id}]}, {"$set": {"rate": rate}})
        await get_options_color(color, callback_query.from_user.id)
        await row_message(callback_query.from_user.id)
        await (mental_rate_strike(callback_query.from_user.id, 'volunteer'))
        collection_name['users'].find().close()
        collection_name['mental_rate'].find().close()
    except (Exception):
        await bot.send_message(callback_query.from_user.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори отправку настроения через несколько минут или напиши разработчикам через команду /feedback")


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

async def get_options_color(color: str, chat_id: int):
    arr = []
    for item in texts.get("polls_answers"):
        if (item.get("color") == color):
            arr.append(item)
    await get_texts_to_send_mood(await rand_select_obj_texts(arr), chat_id)

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

async def row_message(chat_id: int):
    await bot.send_message(chat_id, "Ты уже замерил свое настроение " + str(await how_many_days_user_with_us(chat_id)) + " раз! Продолжай в том же духе 😎")
