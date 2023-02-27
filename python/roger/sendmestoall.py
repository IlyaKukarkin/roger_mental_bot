from aiogram import types

from states import Recording
from aiogram.dispatcher import FSMContext
from database import get_database
from config import bot
from aiogram.utils.exceptions import BotBlocked


async def get_message_to_all(message: types.Message):
    await Recording.AwaitForAMessageForAll.set()
    await bot.send_message(message.chat.id, "Отправь любое сообщение (текст) — и я перешлю его всем пользователям")

async def send_message_to_all(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    if message.text == "/stop":
        await state.finish()
        await bot.send_message(message.chat.id, "Дропнул стейт, отправлять ничего не буду")
        return 
    
    collection_name = get_database()
    user = collection_name["users"].find_one({"telegram_id": str(message.chat.id)}, {
                                             '_id': 1, "form_id": 1, "is_admin": 1})
    if (user["is_admin"] == False):
        await bot.send_message(message.chat.id, "Сорри, ты не админ этого бота. Не расстраивайся, ты же клиент!")
        await state.finish()
        return
    await state.finish()
    users = collection_name["users"].find(
        {"is_active": True}, {'_id': 1, "telegram_id": 1})
    for i in users:
        try: 
            await bot.send_message(int(i["telegram_id"]), message.text)
        except (BotBlocked): #если юзер заблочил бота, не падаем
            print("Юзер " + i["telegram_id"] + "пидор, заблочил бота")
            collection_name = get_database()
            collection_name["users"].find_one_and_update(
                {'_id': i['_id']}, {'is_active': False})
            collection_name['users'].find().close() 
        except (Exception): 
            print ("Failed to send a message to a user " + user['telegram_id'])
    collection_name['users'].find().close()
