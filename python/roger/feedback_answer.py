from aiogram import types
from config import bot
from database import get_database
from states import Recording
from aiogram.types import ParseMode
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import bold, text

async def feedback_answer_start(message: types.Message):
    collection_name = get_database()
    user = collection_name["users"].find_one({"telegram_id": str(message.chat.id)}, {
                                             '_id': 1, "form_id": 1, "is_admin": 1})
    if (user["is_admin"] == False):
        await bot.send_message(message.chat.id, "Сорри, ты не админ этого бота. Не расстраивайся, ты же клиент!")
        return    
    await Recording.AwaitForAnAnswerToFeedback.set()
    await bot.send_message(message.chat.id, "Жду от тебя ответа на фидбек. Пиши его ниже. Не забудь прикрепить реплай, на что именно отвечаем")

async def feedback_send_text_to_user(message: types.Message, state: FSMContext):
    try: 
        await state.update_data(AwaitForAnAnswerToFeedback=message.text)
        if type(message.reply_to_message.text) == type(None):
            mes_str = message.reply_to_message.caption
        else:
            mes_str = message.reply_to_message.text
        feedback_chat_id = mes_str.partition('chat_id: ')[2].partition('.')[0]
        feedback_message_id = mes_str.partition('message_id: ')[2].partition('.')[0]
        await bot.send_message(int(feedback_chat_id), text(bold("Разработчик прислал ответ на твой фидбек: \n\n")) + message.text, reply_to_message_id=int(feedback_message_id), parse_mode=ParseMode.MARKDOWN)
        await bot.send_message(message.chat.id, "Ответ на фидбек отправлен")
    except:
        await bot.send_message(message.chat.id, "Не получилось отправить. Сделай все заново")
    await state.finish()

