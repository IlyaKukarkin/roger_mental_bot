from aiogram import types
from config import bot
from database import get_database
from states import Recording
from aiogram.types import ParseMode
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import bold, text
import openai, os,sys
from keyboards import ask_for_rate_messages_support
from database import get_database
import datetime
from common import delete_keyboard
#from config import chatGPT_token

chatGPT_token = "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" 

async def support_message(message: types.Message):
    await bot.send_message(message.chat.id, "Ты перешел в тестовый режим диалога. Чтобы выйти из него, введи команду /stop. Оставить фидбек или пожаловаться можно по команде /feedback")
    await bot.send_message(message.chat.id, "Что стряслось, друг?")
    await Recording.AwaitForAProblem.set()

async def await_for_a_problem(message: types.Message, state: FSMContext):
   
    await state.update_data(AwaitForAProblem=message.text)
    if message.text == "/stop":
        await state.finish()
        await bot.send_message(message.chat.id, "Ты вышел из режима диалога с ботом. Чтобы вернуться в него снова, вызови команду /support")
        return 
    
    if str(message.text)[0] == '/':
        await bot.send_message(message.chat.id, "Ты находишься в режиме диалога с ботом. Чтобы выйти из него, выбери команду /stop, а затем повторно вызови нужную команду")
        await Recording.AwaitForAProblem.set()
        return
    
    collection_name = get_database()
    id_user_db = collection_name['users'].find_one({"telegram_id": str(message.chat.id)}, {
                                                                    "_id": 1})
    collection_name['support_messages_income'].insert_one({"user_id": id_user_db["_id"], "tg_id_user": message.chat.id, "time_to_send": datetime.datetime.now(), "id_tg_message": message.message_id, "text": message.text})

    try: 
        openai.api_key = chatGPT_token

        completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=message.text,
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.5,
)

        message_text = completions.choices[0].text
        id_message = await bot.send_message(message.chat.id, message_text, reply_markup=ask_for_rate_messages_support)
        
        collection_name['support_messages_outcome'].insert_one({"user_id": id_user_db["_id"], "tg_id_user": message.chat.id, "time_to_send": datetime.datetime.now(), "id_tg_message": id_message.message_id, "text": id_message.text, "rate": None})

        await Recording.AwaitForAProblem.set()
        collection_name['support_messages_income'].find().close() 
        collection_name['support_messages_outcome'].find().close() 
    except Exception as e: 
          await bot.send_message(message.chat.id, "Не получилось обработать запрос. Переформулируй его или попробуй повторить его позже. Ошибка: " + str(e))

    
async def callback_after_click_on_button_support(callback_query: types.CallbackQuery, state: FSMContext, rate: bool):
    await bot.answer_callback_query(callback_query.id, text = 'Спасибо за оценку, bestie ❤️')
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    try:
        collection_name = get_database()
        collection_name["support_messages_outcome"].find_one_and_update(
                {'tg_id_user': callback_query.from_user.id, "id_tg_message": callback_query.message.message_id}, {"$set": {'rate': rate}})
        collection_name['support_messages_outcome'].find().close() 
    except Exception as e: 
          await bot.send_message(callback_query.from_user.id, "Не получилось обработать запрос. Переформулируй его или попробуй повторить его позже. Ошибка: " + str(e))

    