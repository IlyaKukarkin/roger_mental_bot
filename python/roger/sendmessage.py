from aiogram.types import ParseMode
from aiogram import types
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BotBlocked
from common import delete_keyboard, get_options, today_is_the_day
import datetime
from keyboards import kb_for_mental_poll, support_start_keyboard
from database import get_database
from aiogram.dispatcher import FSMContext
from bson import ObjectId
from aiogram.utils.markdown import bold, text
from common import get_pictures, rand_select_obj_texts, Weekdays
from keyboards import ask_for_rate_messages
import requests
from volunteers import mental_rate_strike, how_many_days_user_with_us
import json
import random
import time
from config import contentful_api_readonly_url, contenful_space_id, contenful_access_token, link_to_form, bot
from ratestata import send_rate_stata
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
        if (id_previous_mes):
            await delete_keyboard(chat_id, id_previous_mes['id_tg_message'])
        #await bot.send_message(chat_id, await get_options('greetings'), parse_mode=ParseMode.MARKDOWN)
        id = await bot.send_message(chat_id, await get_options('polls_questions'), parse_mode=ParseMode.MARKDOWN, reply_markup=kb_for_mental_poll)
        collection_name['mental_rate'].insert_one(
            {"rate": 0, "id_user": user['_id'], "date": datetime.datetime.now(), "id_tg_message": id.message_id})
        collection_name['users'].find().close()
        collection_name['mental_rate'].find().close()
    except (BotBlocked):
        print(f"Юзер {chat_id} пидор, заблочил бота")
        collection_name = get_database()
        collection_name["users"].find_one_and_update(
                {'_id': user['_id']}, {"$set": {'is_active': False}})
        collection_name['users'].find().close() 
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
        # 3 is for Thursday
        if today_is_the_day(Weekdays.Thursday, int(user['timezone'])):
            await sunday_send_rate_stata(callback_query.from_user.id)
        await offer_to_chat_with_chatgpt(color, callback_query.from_user.id)
        collection_name['users'].find().close()
        collection_name['mental_rate'].find().close()
    except (Exception):
        await bot.send_message(callback_query.from_user.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори отправку настроения через несколько минут или напиши разработчикам через команду /feedback")


async def create_message_with_support(chat_id: int, cursor: list, user_to_send: ObjectId):
    if cursor['is_anonymous'] == True:
        message = text(bold("Имя: ") + "Аноним" + '\n')
    else:
        message = text(bold("Имя: ") + cursor["user"][0]["name"] + '\n')
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

    # телега не пускает сообщения с этими символами, сделали экранирование вместе 🤝
    cursor['text'] = cursor['text'].replace("_", "\_")
    cursor['text'] = cursor['text'].replace("*", "\*")
    cursor['text'] = cursor['text'].replace("`", "\`")
    cursor['text'] = cursor['text'].replace("[", "\[")

    message = message + text(bold("Сообщение: ") +
                             '\n' + cursor['text'] + '\n')
    message = message + '\n'
    if cursor['media_link'] != "":
        message = message + \
            text(bold("Что стоит глянуть: ") + '\n' + cursor['media_link'])
    try:
        collection_name = get_database()

        id_previous_mes = collection_name['user_messages'].find_one({"id_user": user_to_send}, {
                                                                    "id_user": 1, "id_message": 1, "id_tg_message": 1}, sort=[("time_to_send", -1)])
        if (id_previous_mes != None):
            rate_previous_mes = collection_name['rate'].find_one(
                {"id_message": id_previous_mes['id_message'], 'id_user': id_previous_mes['id_user']})
            if (rate_previous_mes == None):
                await delete_keyboard(chat_id, id_previous_mes['id_tg_message'])
        id_message = await bot.send_message(chat_id, message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True, reply_markup=ask_for_rate_messages)
        
        print("\n")
        print('USER_MESSAGES -> ты увидел сообщение')
        print({"id_user": user_to_send, "id_message": cursor["_id"], "time_to_send": datetime.datetime.now(), "id_tg_message": id_message.message_id})
        
        collection_name['user_messages'].insert_one({"id_user": user_to_send, "id_message": cursor["_id"], "time_to_send": datetime.datetime.now(), "id_tg_message": id_message.message_id})
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
    print(gif_link)
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
                user_id = collection_name["users"].find_one(
                    {"telegram_id": str(chat_id)}, {'_id': 1, 'name': 1})

                print("\n")
                print("Пользователь, кому отправляем сообщение")
                print(user_id["_id"])

                message = collection_name["messages"].aggregate([
                    {
                        '$match': {
                            'is_approved': True,
                            'id_user': {
                                '$ne': ObjectId(str(user_id['_id']))
                            }
                        }
                    }, {
                        '$lookup': {
                            'from': 'user_messages',
                            'localField': '_id',
                            'foreignField': 'id_message',
                            'pipeline': [
                                {
                                    '$match': {
                                        'id_user': ObjectId(str(user_id['_id']))
                                    }
                                }
                            ],
                            'as': 'sended'
                        }
                    }, {
                        '$match': {
                            'sended': {
                                '$not': {
                                    '$size': 1
                                }
                            }
                        }
                    }, {
                        '$sample': {
                            'size': 1
                        }
                    }, {
                        '$lookup': {
                            'from': 'users',
                            'localField': 'id_user',
                            'foreignField': '_id',
                            'as': 'user'
                        }
                    }
                ])

                message_list = list(message)

                print("\n")
                print("Сообщение для показа")
                print(message_list)

                if (len(message_list) != 0):
                    await create_message_with_support(chat_id, message_list[0], user_id["_id"])
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


async def offer_to_chat_with_chatgpt(color: str, user_id: int):
    if (color in ['red', 'orange']):
        await bot.send_message(user_id, "Как насчет поболтать со мной? Я могу поддержать диалог: умею распознавать проблемы и давать осмысленные ответы. Попробуем?", reply_markup = support_start_keyboard)
    return


async def sunday_send_rate_stata(chat_id: int):
    """A non-destructive modification of send_rate stata for the purposes of sending weekly stata after a user
    has rated their mood on a Sunday.
    Sends a message from a collection of specially manufactured texts and then
    sends mental state statistics for the past week."""
    mes = await rand_select_obj_texts(texts.get('mental_week_stata'))
    await bot.send_message(chat_id, mes['text'])
    await send_rate_stata(str(chat_id), 'week')
