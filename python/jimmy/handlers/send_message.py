from bson import ObjectId
from aiogram.utils.exceptions import BotBlocked
from pymongo import MongoClient
from bson import ObjectId
import certifi
from amplitude import BaseEvent

import os
from singleton import Bot
from singleton import Amplitude
from db.users import Users
from db.messages import Messages
from db.user_messages import User_Messages
from utils.message import send_message
from utils.keyboards import delete_keyboard
from utils.amplitude import user_to_string, message_to_string

db_token = os.getenv("MONGODB_URI")


def get_database():
    client = MongoClient(db_token, tlsCAFile=certifi.where())
    collection_name = client["roger-bot-db"]
    return collection_name


async def send_message_to_rate():
    bot = Bot().get_bot()
    users = Users()
    messages = Messages()
    user_messages = User_Messages()
    amplitude = Amplitude().get_amplitude()

    try:
        users_to_send = users.get_all_volunteers_by_time()

        for user in users_to_send:
            user_id = ObjectId(str(user['_id']))

            sent_today = user_messages.get_already_sended_messages(user_id)
            if (len(list(sent_today)) == 0):
                print('Отправляю пользователю: ' + str(user['_id']))

                message_to_rate = messages.get_unapproved_by_user(user_id)

                message_list = list(message_to_rate)

                if (len(message_list) != 0):
                    old_messages = user_messages.get_not_rated_massages(
                        user_id)

                    for old_message in old_messages:
                        await delete_keyboard(user['telegram_id'], old_message['id_tg_message'])

                    message_to_send = message_list[0]

                    print('Отправляю сообщение: ' + str(message_to_send))

                    await bot.send_message(str(user['telegram_id']), "Привет 👋\nОцени, пожалуйста, это сообщение от пользователя:")

                    tg_message_id = await send_message(str(user['telegram_id']), message_to_send)

                    amplitude.track(
                        BaseEvent(
                            event_type="Sending message to rate",
                            user_id=str(user_id),
                            event_properties={
                                "user": user_to_string(user),
                                "message": message_to_string(message_to_send)
                            }
                        )
                    )

                    user_messages.insert_user_message(user_id, ObjectId(
                        str(message_to_send['_id'])), tg_message_id)
    except (BotBlocked):
        print(f"Юзер 'хуй знает кто' пидор, заблочил бота")
        collection_name = get_database()
        collection_name["users"].find_one_and_update(
            {'_id': user_id}, {"$set": {'is_volunteer': False}})
        collection_name['users'].find().close()
    except Exception as e:
        print(e)
