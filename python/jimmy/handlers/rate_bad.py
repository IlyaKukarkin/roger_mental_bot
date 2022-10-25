from aiogram import types
from aiogram.dispatcher import FSMContext

from singleton import Bot
from db.rate import Rate
from db.user_messages import User_Messages
from utils.message import send_message
from utils.keyboards import delete_keyboard


async def rate_bad_handler(callback_query: types.CallbackQuery, state: FSMContext):
    bot = Bot().get_bot()
    rate = Rate()
    user_messages = User_Messages()

    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)

    message_to_update = user_messages.get_user_message_by_tg_id(
        callback_query.message.message_id)

    rate.insert_rate(message_to_update["id_user"],
                     message_to_update["id_message"], False)

    await bot.send_message(callback_query.from_user.id, "Спасибо за оценку!")
