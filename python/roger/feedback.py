from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards import feedback_keyboard, feedback_finish_keyboard
from aiogram.types import ParseMode

from database import get_database
from states import Recording
from common import delete_keyboard
from config import dp, bot

async def feedback_start(message: types.Message):
    await bot.send_message(message.chat.id, 
                          "Отлично! Приступаем к созданию фидбека?\nЕсли ты передумал отправлять фидбек, просто не нажимай на кнопку ниже", parse_mode=ParseMode.MARKDOWN, reply_markup = feedback_keyboard)

@dp.callback_query_handler(lambda c: c.data == 'feedback_start')
async def rate_stata_handler_week2(callback_query: types.CallbackQuery):
    await callback_query.answer("Не передавай конфиденциальные данные")
    await feedback_getting(callback_query.from_user.id, callback_query.message.message_id)

async def feedback_getting(chat_id: int, message_id: int):
    await delete_keyboard(chat_id, message_id)
    await bot.send_message(chat_id, 
                          "Ты перешел в режим отправки фидбека. Ниже отправь любое сообщение (текст или фото) — и я перешлю его разработчикам.\n\nЕсли ты передумал, нажми на кнопку ниже — и я ничего не отправлю", parse_mode=ParseMode.MARKDOWN, reply_markup = feedback_finish_keyboard)
    await Recording.AwaitForAFeedback.set()

@dp.callback_query_handler(lambda c: c.data == 'feedback_finish', state=Recording.AwaitForAFeedback)
async def feedback_finish_def(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, "Ты вышел из режима отправки фидбека. Если захочешь вернуться и написать фидбек разработчикам, вызови команду /feedback")
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == 'feedback_finish')
async def feedback_finish_def(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    return

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
            "Новый фидбек от пользователя " + user['telegram_username'] + ' из RogerMentalBot.\n\nchat_id: ' + str(message.chat.id) + '.\nmessage_id: ' + str(message.message_id) + '.\n\nТекст сообщения:\n"' + message.text + '"')
    await bot.send_message(message.chat.id, "Сообщение улетело разработчикам. Спасибо! 😍")
    collection_name['users'].find().close()    
    await state.finish()

#получаем фото от пользователя и пересылаем админам
async def feedback_get_photo_from_user(message: types.Message, state: FSMContext):
    await state.update_data(name=message.caption)
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
        message_caption = message.caption
        if (message_caption == None):
            message_caption = "Отправлено без подписи"
        await bot.send_photo(id['telegram_id'], photo=message.photo[-1].file_id, caption='chat_id: ' + str(message.chat.id) + '.\nmessage_id: ' + str(message.message_id) + '.\n\nТекст сообщения: "' + message_caption + '"')
    await bot.send_message(message.chat.id, "Сообщение улетело разработчикам. Спасибо! 😍")
    collection_name['users'].find().close()    
    await state.finish()



    
