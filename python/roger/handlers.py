import datetime
from aiogram import types, dispatcher
from database import get_database
from variables import botClient
import pytz
from common import delete_keyboard


async def rate_message(callback_query: types.CallbackQuery, state: dispatcher.FSMContext, rate: bool):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    try:
        collection_name = get_database()
        message_to_update = collection_name['user_messages'].find_one(
            {"id_tg_message": callback_query.message.message_id}, {"_id": 0, "id_message": 1, "id_user": 1})

        print("\n")
        print("RATE -> ты оценил сообщение")
        print(message_to_update)
        print(rate)

        collection_name['rate'].insert_one({"id_user": message_to_update["id_user"],
                                           "id_message": message_to_update["id_message"], "rate": rate, "time_to_send": datetime.datetime.now(pytz.utc)})
        print("written")
        collection_name['rate'].find().close()
        collection_name['user_messages'].find().close()
        await callback_query.answer("Спасибо за оценку ❤️")
    except (Exception):
        await botClient.send_message(callback_query.from_user.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори действие через несколько минут или напиши разработчикам через команду /feedback")
