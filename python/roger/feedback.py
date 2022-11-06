from aiogram import types
from aiogram.dispatcher import FSMContext

from database import get_database
from states import Recording
from config import bot

#переводим пользователя в стейт ожидания сообщения
async def feedback_command(message: types.Message):
    await bot.send_message(message.chat.id, 
                          "Отправь любое сообщение (текст или фото) — и я перешлю его разработчикам")
    await Recording.AwaitForAFeedback.set()

#получаем текстовый фидбек от пользователя и пересылаем админам
async def feedback_get_text_from_user(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    collection_name = get_database()
    #поиск ника пользователя для отображения в сообщении
    user = collection_name["users"].find_one(
        {'telegram_id': str(message.chat.id)}, {'telegram_username': 1})
    #поиск админов для отправки фидбека
    admins = collection_name["users"].find({"is_admin": True, "is_active": True}, 
        {'_id': 0, 'telegram_id': 1})
    #отправка сообщения всем админам
    for id in admins:
        await bot.send_message(id["telegram_id"], 
            "Новый фидбек от пользователя " + user['telegram_username'] + ' из RogerBot. Вот, что он пишет: \n\n"' + message.text + '"')
    await bot.send_message(message.chat.id, "Сообщение улетело разработчикам. Спасибо! 😍")
    collection_name['users'].find().close()    
    await state.finish()

#получаем фото от пользователя и пересылаем админам
async def feedback_get_photo_from_user(message: types.Message, state: FSMContext):
    collection_name = get_database()
    #поиск ника пользователя для отображения в сообщении
    user = collection_name["users"].find_one(
        {'telegram_id': str(message.chat.id)}, {'telegram_username': 1})
    #поиск админов для отправки фидбека
    admins = collection_name["users"].find({"is_admin": True, "is_active": True}, 
        {'_id': 0, 'telegram_id': 1})
    #отправка сообщения всем админам
    for id in admins:
        await bot.send_message(id['telegram_id'], 
            "Новое фото от пользователя " + user['telegram_username'] + '. Вот оно:')
        await bot.send_photo(id['telegram_id'], photo=message.photo[-1].file_id)
    await bot.send_message(message.chat.id, "Сообщение улетело разработчикам. Спасибо! 😍")
    collection_name['users'].find().close()    
    await state.finish()
