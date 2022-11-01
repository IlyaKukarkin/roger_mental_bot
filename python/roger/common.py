import requests
import json
import random
from bson import ObjectId
from database import get_database
import datetime
import pytz
from config import bot, contentful_api_readonly_url, contenful_access_token, contenful_space_id

# read texts from json file
with open('texts.json') as t:
    texts = json.load(t)

#удаляем клавиатуру у сообщения после клика пользователя по ней
async def delete_keyboard(chat_id: int, message_id: int):
    try:
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
    except (Exception):
        return

#получить картинку из хранилища по id
async def get_pictures(picture_id: str):
    response = requests.get(contentful_api_readonly_url + 'spaces/' + contenful_space_id +
                            '/environments/master/assets/' + picture_id + '?access_token=' + contenful_access_token)
    answer = json.loads(response.content)
    answer = answer.get("fields").get("file").get("url")
    return str(answer[2:])

#получить массив текстов из json
async def get_options(array: str):
    arr = []
    for item in texts.get(array):
        arr.append(item)
    s = await rand_select_obj_texts(arr)
    return s.get('text')

#получить частоту текстов из json
async def rand_select_obj_texts(arr: list):
    rand_id_array = []
    j = 0
    for item in arr:
        for i in range(item.get("frequency")):
            rand_id_array.append(j)
        j += 1
    return arr[rand_id_array[random.randint(0, len(rand_id_array) - 1)]]

#проверить валидность имени пользователя перед добавлением его в базу (исключаем вариант, когда username в телеграме не задан)
async def check_id_username_is_valid_before_save(username: str):
    if (username == None):
        return ""
    return username

#проверяем, была ли отправка сообщения пользователю сегодня
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