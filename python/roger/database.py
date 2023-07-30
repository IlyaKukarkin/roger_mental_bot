from pymongo import MongoClient
from bson import ObjectId
import datetime
import certifi
from reg.after_registration import create_new_message_after_registration
from config import bot, db_token

#подключаемся к бд
def get_database():
    client = MongoClient(db_token, tlsCAFile=certifi.where())
    collection_name = client["roger-bot-db"]
    return collection_name

#создаем нового пользователя в бд
async def create_new_user(tg_username: str, username: str, time_zone: str, telegram_id: str, user_time: str):
    try:
        collection_name = get_database()
        form_id = ObjectId()
        if tg_username != "":
            tg_username = "@" + tg_username
        else:
            tg_username = " "
        collection_name['users'].insert_one({"telegram_username": tg_username, "name": username, "timezone": time_zone, "is_volunteer": False, "is_banned_from_volunteering": False,
                                            "form_id": form_id, "telegram_id": telegram_id, "is_admin": False, "is_active": True, "created_at": datetime.datetime.now(), "time_to_send_messages": user_time})
        await bot.send_message(int(telegram_id), "Отлично! 😍")
        collection_name['users'].find().close()
        await create_new_message_after_registration(telegram_id, username, form_id)
    except (Exception):
        await bot.send_message(int(telegram_id), "Ой, кажется, что-то пошло не так 😞 \nПовтори действие через несколько минут или напиши разработчикам через команду /feedback")

async def search_user_by_nickname (tg_username: str, telegram_id: str):
    try: 
        collection_name = get_database()
        friend = collection_name['users'].find_one({"telegram_username": tg_username})
        collection_name['users'].find().close()
        return friend
    except (Exception):
        await bot.send_message(int(telegram_id), "Ой, кажется, что-то пошло не так 😞 \nПовтори действие через несколько минут или напиши разработчикам через команду /feedback")

async def send_friends_request(tg_id_friend_to: int, friend2: list):
    try:
        collection_name = get_database()
        user = await search_user_by_tg_id(tg_id_friend_to)
        collection_name['friends'].insert_one({"from": user['_id'], "to": friend2['_id'], "request_sent_time": datetime.datetime.now(), "status": 0})
        collection_name['friends'].find().close()
        await notify_a_friend_about_friends_request(user['telegram_username'], user['name'], int(friend2['telegram_id']))
    except (Exception):
        await bot.send_message(int(tg_id_friend_to), "Ой, кажется, что-то пошло не так 😞 \nПовтори регистрацию командой /start через несколько минут или напиши разработчикам через команду /feedback")

async def search_user_by_tg_id(tg_id: int):
    try: 
        collection_name = get_database()
        user = collection_name["users"].find_one(
                {"telegram_id": str(tg_id)}, {'_id': 1, 'name': 1, 'telegram_username': 1})
        collection_name['users'].find().close()
        return user
    except (Exception):
        await bot.send_message(int(tg_id), "Ой, кажется, что-то пошло не так 😞 \nПовтори действие через несколько минут или напиши разработчикам через команду /feedback")

async def notify_a_friend_about_friends_request(tg_nickname_friend_from: str, tg_name_friend_from: str, tg_id_friend_to: int):
    await bot.send_message(int(tg_id_friend_to), "Тебе пришел запрос на дружбу от пользователя " + tg_name_friend_from + " (" + tg_nickname_friend_from + ")")

async def is_user_active(id_user: int):
    try: 
        collection_name = get_database()
        user = collection_name["users"].find_one(
                {"telegram_id": str(id_user)}, {'_id': 1, 'is_active': 1})
        collection_name['users'].find().close()
        return user['is_active']
    except (Exception):
        await bot.send_message(int(id_user), "Ой, кажется, что-то пошло не так 😞 \nПовтори действие через несколько минут или напиши разработчикам через команду /feedback")

async def search_user_by_object_id(id: ObjectId):
    try: 
        collection_name = get_database()
        user = collection_name["users"].find_one(
                {"_id": id}, {'_id': 1, 'name': 1, 'telegram_username': 1, "telegram_id": 1})
        collection_name['users'].find().close()
        return user
    except (Exception):
        return None
