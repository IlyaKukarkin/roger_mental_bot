from aiogram import types
from config import bot
from database import get_database
from states import Recording
from aiogram.dispatcher import FSMContext
import openai
from openai.error import RateLimitError 
from keyboards import ask_for_rate_messages_support
from database import get_database
import datetime
from common import delete_keyboard
from config import chatGPT_token

from classes.chatgpt_arrays import ArrayOfChats

array_of_chats = ArrayOfChats()


async def support_message(message: types.Message):
    await bot.send_message(message.chat.id, "Ты перешел в режим диалога. Чтобы выйти из него, введи команду /stop. Оставить фидбек или пожаловаться на бота можно по команде /feedback\n\nДисклеймер: ответы генерируются автоматически и могут быть несовершенны. Если у тебя возникли серьезные проблемы, пожалуйста, обратись к следующим организациям:\n\n1. Служба психологической поддержки: 8 (800) 333-44-34\n2. Региональные номера телефонов служба поддержки: [ссылка](https://secretmag.ru/survival/telefony-besplatnoi-psikhologicheskoi-pomoshi-v-rossii.htm)", parse_mode="Markdown", disable_web_page_preview=True)
    await bot.send_message(message.chat.id, "Что стряслось, друг?")
    array_of_chats.add_message (message.chat.id, {'role': 'assistant', 'content': 'Отвечай от имени Роджера. Это бот, который поддерживает людей с плохим настроением'})

    await Recording.AwaitForAProblem.set()

async def support_callback(callback_query: types.CallbackQuery):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, "Ты перешел в тестовый режим диалога. Чтобы выйти из него, введи команду /stop. Оставить фидбек или пожаловаться можно по команде /feedback")
    await bot.send_message(callback_query.from_user.id, "Что стряслось, друг?")
    array_of_chats.add_message (callback_query.from_user.id, {'role': 'assistant', 'content': 'Отвечай от имени Роджера. Это бот, который поддерживает людей с плохим настроением'})
    await Recording.AwaitForAProblem.set()

async def await_for_a_problem(message: types.Message, state: FSMContext):
    await state.update_data(AwaitForAProblem=message.text)
    if message.text == "/stop":
        await state.finish()
        array_of_chats.delete_array(message.chat.id)
        await bot.send_message(message.chat.id, "Ты вышел из режима диалога. Чтобы вернуться в него снова, вызови команду /support")
        return 
    
    if str(message.text)[0] == '/':
        await bot.send_message(message.chat.id, "Ты находишься в режиме диалога. Чтобы выйти из него, выбери команду /stop, а затем повторно вызови нужную команду")
        await Recording.AwaitForAProblem.set()
        return

    try: 
        openai.api_key = chatGPT_token
        collection_name = get_database()
        id_user_db = collection_name['users'].find_one({"telegram_id": str(message.chat.id)}, {
                                                                    "_id": 1})
        collection_name['support_messages_income'].insert_one({"user_id": id_user_db["_id"], "tg_id_user": message.chat.id, "time_to_send": datetime.datetime.now(), "id_tg_message": message.message_id, "text": message.text})

        role = "user"
        mes = message.text.replace('\n', ' ')
        answer = {'role': role, 'content': mes}
        array_of_chats.add_message(message.chat.id, answer)
        completions = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=array_of_chats.get_chat(message.chat.id)

)
        message_text = str(completions.choices[0].message.content).encode('unicode_escape').decode('unicode_escape', 'ignore')

        id_message = await bot.send_message(message.chat.id, message_text, reply_markup=ask_for_rate_messages_support)
        role = "assistant"
        answer = {'role': role, 'content': message_text}
        array_of_chats.add_message(message.chat.id, answer)
        collection_name['support_messages_outcome'].insert_one({"user_id": id_user_db["_id"], "tg_id_user": message.chat.id, "time_to_send": datetime.datetime.now(), "id_tg_message": id_message.message_id, "text": id_message.text, "rate": None})

        await Recording.AwaitForAProblem.set()
        collection_name['support_messages_income'].find().close() 
        collection_name['support_messages_outcome'].find().close() 
    except RateLimitError:
        await bot.send_message(message.chat.id, "Бот сейчас перегружен запросами 😿 Подожди 10 секунд и повтори свой вопрос")
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


