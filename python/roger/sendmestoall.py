from aiogram import types

from states import Recording
from aiogram.dispatcher import FSMContext
from database import get_database
from config import bot


async def get_message_to_all(message: types.Message):
    await Recording.AwaitForAMessageForAll.set()
    await bot.send_message(message.chat.id, "Отправь любое сообщение (текст или фото) — и я перешлю его всем пользователям")

async def send_message_to_all(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    collection_name = get_database()
    user = collection_name["users"].find_one({"telegram_id": str(message.chat.id)}, {
                                             '_id': 1, "form_id": 1, "is_admin": 1})
    if (user["is_admin"] == False):
        await bot.send_message(message.chat.id, "Сорри, ты не админ этого бота. Не расстраивайся, ты же клиент!")
        await state.finish()
        return
    users = collection_name["users"].find(
        {"is_active": True}, {'_id': 1, "telegram_id": 1, "is_admin": 1})
    for i in users:
        await bot.send_message(i["telegram_id"], message.text)
    await state.finish()
    collection_name['users'].find().close()