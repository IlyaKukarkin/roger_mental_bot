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
        collection_name['users'].insert_one({"telegram_username": "@" + tg_username, "name": username, "timezone": time_zone, "is_volunteer": False, "is_banned_from_volunteering": False,
                                            "form_id": form_id, "telegram_id": telegram_id, "is_admin": False, "is_active": True, "created_at": datetime.datetime.now(), "time_to_send_messages": user_time})
        await bot.send_message(int(telegram_id), "Отлично! 😍")
        collection_name['users'].find().close()
        await create_new_message_after_registration(telegram_id, username, form_id)
    except (Exception):
        await bot.send_message(int(telegram_id), "Ой, кажется, что-то пошло не так 😞 \nПовтори регистрацию командой /start через несколько минут или напиши разработчикам через команду /feedback")
