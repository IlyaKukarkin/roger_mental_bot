from pymongo import MongoClient
from bson import ObjectId
import datetime
import certifi
from reg.after_registration import create_new_message_after_registration
from config import bot, db_token
from aiogram.types import InlineKeyboardButton
from keyboards import friend_request_kb
from aiogram.utils.markdown import link
from aiogram.utils.callback_data import CallbackData


call_back_approve = CallbackData("Approve", "id", "friend")
call_back_decline = CallbackData("Decline", "id", "friend")

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
        if check_if_user_has_username(user['telegram_username']) == False:
            user['telegram_username'] = change_empty_username_to_a_link(int(user['telegram_id']), user['name'])
        await notify_a_friend_about_friends_request(user['telegram_username'], user['name'], int(friend2['telegram_id']), user['telegram_id'])
    except (Exception):
        await bot.send_message(int(tg_id_friend_to), "Ой, кажется, что-то пошло не так 😞 \nПовтори регистрацию командой /start через несколько минут или напиши разработчикам через команду /feedback")

async def check_if_user_sent_request(tg_id_friend_from: int, tg_id_friend_to: ObjectId):
    try:
        collection_name = get_database()
        user_from = await search_user_by_tg_id(tg_id_friend_from)
        friend_request = collection_name["friends"].find_one({"from": user_from['_id'], "to": tg_id_friend_to, "status": {'$lt': 2}}, {'_id': 1, 'status': 1})
        collection_name['friends'].find().close()
        return friend_request
    except (Exception):
        await bot.send_message(tg_id_friend_from, "Ой, кажется, что-то пошло не так 😞 \nПовтори регистрацию командой /start через несколько минут или напиши разработчикам через команду /feedback")

async def check_if_user_got_request(tg_id_friend_to: int, tg_id_friend_from: ObjectId):
    try:
        collection_name = get_database()
        user_to = await search_user_by_tg_id(tg_id_friend_to) 
        friend_request = collection_name["friends"].find_one({"from": tg_id_friend_from, "to": user_to['_id'], "status": {'$lt': 2}}, {'_id': 1, 'status': 1})
        collection_name['friends'].find().close()
        return friend_request
    except (Exception):
        await bot.send_message(tg_id_friend_to, "Ой, кажется, что-то пошло не так 😞 \nПовтори регистрацию командой /start через несколько минут или напиши разработчикам через команду /feedback")

async def find_all_friends(user: list, id_user: int):
    try:
        collection_name = get_database()
        friends_for_return = []
        friends = collection_name["friends"].find({"from": user['_id'], "status": 1}, {'_id': 0, 'to': 1})
        friends = list(friends)
        for x in friends:
            friends_for_return.append(x["to"])
        friends1 = collection_name["friends"].find({"to": user['_id'], "status": 1}, {'_id': 0, 'from': 1})
        friends1 = list(friends1)
        for x in friends1:
            friends_for_return.append(x["from"])
        collection_name['friends'].find().close()
        return friends_for_return
    except (Exception):
        await bot.send_message(id_user, "Ой, кажется, что-то пошло не так 😞 \nПовтори регистрацию командой /start через несколько минут или напиши разработчикам через команду /feedback")

async def search_user_by_tg_id(tg_id: int):
    try: 
        collection_name = get_database()
        user = collection_name["users"].find_one(
                {"telegram_id": str(tg_id)}, {'_id': 1, 'name': 1, 'telegram_username': 1, 'telegram_id': 1})
        collection_name['users'].find().close()
        return user
    except (Exception):
        await bot.send_message(int(tg_id), "Ой, кажется, что-то пошло не так 😞 \nПовтори действие через несколько минут или напиши разработчикам через команду /feedback")

async def notify_a_friend_about_friends_request(tg_nickname_friend_from: str, tg_name_friend_from: str, tg_id_friend_to: int, f: str):
    friend_request_kb_approve = InlineKeyboardButton('✅', callback_data=call_back_approve.new(id='friend_approve', friend=f))
    friend_request_kb_decline = InlineKeyboardButton('❌', callback_data=call_back_decline.new(id='friend_decline', friend=f))
    friend_request_kb.add(friend_request_kb_approve, friend_request_kb_decline)
    await bot.send_message(int(tg_id_friend_to), "Тебе пришел запрос на дружбу от пользователя " + tg_name_friend_from + " (" + tg_nickname_friend_from + ")", reply_markup=friend_request_kb)

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
    
async def accept_decline_friend_request(user: int, friend: int, approve: bool):
    try:
        if approve == True: 
            status = 1
        else: 
            status = 2
        collection_name = get_database()
        user_to = await search_user_by_tg_id(user) 
        user_from = await search_user_by_tg_id(friend)
        collection_name["friends"].find_one_and_update({"from": user_from["_id"], "to": user_to['_id'], "status": 0}, {"$set": {'status': status}})
        collection_name['friends'].find().close()
        return user_from
    except (Exception):
        await bot.send_message(user, "Ой, кажется, что-то пошло не так 😞 \nПовтори регистрацию командой /start через несколько минут или напиши разработчикам через команду /feedback")

def check_if_user_has_username (username: str):
    return (username != '@' and username != ' ' and username != '')
    
def change_empty_username_to_a_link (user_id: int, name: str):
    return link(name, f"tg://user?id={user_id}")