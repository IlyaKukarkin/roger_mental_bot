import requests
import json
import random
from bson import ObjectId
from database import get_database
import datetime
import pytz
from config import bot, contentful_api_readonly_url, contenful_access_token, contenful_space_id
from enum import IntEnum

# read texts from json file
with open('texts.json') as t:
    texts = json.load(t)

# удаляем клавиатуру у сообщения после клика пользователя по ней


async def delete_keyboard(chat_id: int, message_id: int):
    try:
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
    except (Exception):
        print ("failed to delete keyboard")
        return

# получить картинку из хранилища по id


async def get_pictures(picture_id: str):
    response = requests.get(contentful_api_readonly_url + 'spaces/' + contenful_space_id +
                            '/environments/master/assets/' + picture_id + '?access_token=' + contenful_access_token)
    answer = json.loads(response.content)
    answer = answer.get("fields").get("file").get("url")
    return str(answer[2:])

# получить массив текстов из json


async def get_options(array: str):
    arr = []
    for item in texts.get(array):
        arr.append(item)
    s = await rand_select_obj_texts(arr)
    return s.get('text')

# получить частоту текстов из json


async def rand_select_obj_texts(arr: list):
    rand_id_array = []
    j = 0
    for item in arr:
        for i in range(item.get("frequency")):
            rand_id_array.append(j)
        j += 1
    return arr[rand_id_array[random.randint(0, len(rand_id_array) - 1)]]

# проверить валидность имени пользователя перед добавлением его в базу (исключаем вариант, когда username в телеграме не задан)


async def check_id_username_is_valid_before_save(username: str):
    if (username == None):
        return ""
    return username

# проверяем, была ли отправка сообщения пользователю сегодня


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


async def check_if_delete_mental_keyboard(user_id: ObjectId):
    collection_name = get_database()
    mental_hours = collection_name['mental_rate'].aggregate(
        [
            {
                '$match': {
                    'id_user': user_id
                }
            }, {
                '$match': {
                    'rate': 0
                }
            }, {
                '$addFields': {
                    'datetime_now': datetime.datetime.now(pytz.utc)
                }
            }, {
                '$addFields': {
                    'date_diff': {
                        '$dateDiff': {
                            'startDate': '$date',
                            'endDate': '$datetime_now',
                            'unit': 'hour'
                        }
                    }
                }
            }, {
                '$sort': {
                    'date_diff': 1
                }
            }, {
                '$limit': 1
            }
        ]
    )
    mental_hours_clone = list(mental_hours)
    print (mental_hours_clone)
    if (mental_hours_clone):
        if (mental_hours_clone[0]['date_diff']):
            if (mental_hours_clone[0]['date_diff'] == 3):
                user = collection_name["users"].find_one(
                    {"_id": user_id}, {'telegram_id': 1})
                await bot.send_message(int(user['telegram_id']), await get_options('hurry_up_message'))
                collection_name['users'].find().close()

            if (mental_hours_clone[0]['date_diff'] == 12):
                user = collection_name["users"].find_one(
                    {"_id": user_id}, {'telegram_id': 1})
                await delete_keyboard(int(user['telegram_id']), int(list(mental_hours_clone)[0]['id_tg_message']))
                collection_name['users'].find().close()
    collection_name['mental_rate'].find().close()


class Weekdays(IntEnum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6


def today_is_the_day(day: Weekdays, timezone_offset: int):
    """A function that checks whether today is a particular weekday (specified by day parameter)
    considering the timezone offset"""
    delta = datetime.timedelta(hours=timezone_offset)
    tz = datetime.timezone(delta)
    date = datetime.datetime.now(tz)
    return date.weekday() == day
