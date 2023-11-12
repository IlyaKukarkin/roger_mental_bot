import time
from aiogram import types

from states import Registration
from database import get_database
from keyboards import ask_for_name_kb
from config import botClient


async def start_command(message: types.Message):
    collection_name = get_database()
    user = collection_name["users"].find_one(
        {"telegram_id": str(message.chat.id)}, {'_id': 1, 'name': 1, "is_active": 1})
    if (user is not None and user["is_active"]):
        await botClient.send_message(message.chat.id, "Кажется, мы уже знакомы, " + user['name'])
    elif (user is not None and not user["is_active"]):
        await botClient.send_message(message.chat.id, "Здорово, что ты вернулся, " + user['name'] + " 😍")
        collection_name = get_database()
        collection_name["users"].find_one_and_update(
            {'_id': user['_id']}, {"$set": {'is_active': True}})
        collection_name['users'].find().close()
    else:
        await botClient.send_message(message.chat.id, "Привет 👋 \n \nЯ Роджер — бот для твоей кукухи.")
        time.sleep(1)
        await botClient.send_message(message.chat.id, """Каждый вечер я буду интересоваться твоим настроением. \nЯ умею распознавать 4 настроения: \n
🟢 — день был великолепен, лучше и представить нельзя
🟡 — вариант для хорошего дня, в котором были небольшие неприятности
🟠 — день мог бы быть сильно лучше, но еще не все потеряно
🔴 — день был хуже некуда, тебе срочно нужна поддержка
        """)
        time.sleep(6)
        await botClient.send_message(message.chat.id, "Если ты выберешь 🟠 и 🔴 настроение, тогда и начнется самое интересное 🙃 \nЯ подберу тебе ободряющее сообщение от другого пользователя, у которого настроение было отличным — и он захотел поделиться им с тобой")
        time.sleep(5)
        await botClient.send_message(message.chat.id, "И наоборот — если у тебя выдался 🟢 и 🟡 день, то ты сможешь написать свое позитивное сообщение.  \nКогда твое сообщение пройдет модерацию, я буду показывать его тем, кому это сейчас важно")
        time.sleep(5)
        await botClient.send_message(message.chat.id, "Вот такая простая магия ✨")
        time.sleep(3)
        await botClient.send_message(message.chat.id, "Давай познакомимся с тобой поближе! Только будь внимателен — зарегистрироваться можно только один раз 🙃")
        time.sleep(2)
        await botClient.send_message(message.chat.id, "Тебя зовут " + message.from_user.first_name + "? Подтверди свое имя или введи другое", reply_markup=ask_for_name_kb)
        await Registration.Name.set()
        collection_name['users'].find().close()
