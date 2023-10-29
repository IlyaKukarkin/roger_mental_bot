from aiogram import types
from aiogram.dispatcher import FSMContext
from amplitude import BaseEvent

from db.rate import Rate
from db.user_messages import User_Messages
from db.users import Users
from utils.keyboards import delete_keyboard
from utils.amplitude import user_to_string, user_message_to_string
from handlers.rate import send_one_more_message_to_rate
from singleton import Amplitude


async def rate_bad_handler(callback_query: types.CallbackQuery, state: FSMContext):
    rate = Rate()
    user_messages = User_Messages()
    users = Users()
    amplitude = Amplitude().get_amplitude()

    telegram_id = callback_query.from_user.id
    message_id = callback_query.message.message_id

    user = users.get_user_by_telegram_id(str(telegram_id))
    user_id = str(user['_id'])

    await delete_keyboard(telegram_id, message_id)

    message_to_update = user_messages.get_user_message_by_tg_id(message_id)

    rate.insert_rate(message_to_update["id_user"],
                     message_to_update["id_message"], False)

    amplitude.track(
        BaseEvent(
            event_type="Rate message - bad",
            user_id=user_id,
            event_properties={
                "user_id": user_id,
                "message_id": message_id,
                "user": user_to_string(user),
                "message": user_message_to_string(message_to_update)
            }
        )
    )

    await callback_query.answer("Спасибо за оценку ❤️")
    await send_one_more_message_to_rate(telegram_id)
