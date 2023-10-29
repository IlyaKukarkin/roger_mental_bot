from aiogram import types
from bson import ObjectId
from amplitude import BaseEvent

from singleton import Amplitude
from singleton import Bot
from db.users import Users
from db.app_settings import App_Settings
from db.user_messages import User_Messages
from db.messages import Messages
from utils.message import send_message
from utils.keyboards import delete_keyboard
from utils.amplitude import user_to_string, message_to_string


async def rate_handler(message: types.Message):
    await send_one_more_message_to_rate(message.chat.id)


async def send_one_more_message_to_rate(chat_id: int):
    bot = Bot().get_bot()
    users = Users()
    user_messages = User_Messages()
    app_settings = App_Settings()
    amplitude = Amplitude().get_amplitude()

    user = users.get_user_by_telegram_id(str(chat_id))
    user_id = str(user['_id'])

    if (not user['is_volunteer']):
        amplitude.track(
            BaseEvent(
                event_type="Rate message error",
                user_id=user_id,
                event_properties={
                    "user": user_to_string(user),
                    "error": {
                        "message": "Not volunteer"
                    }
                }
            )
        )
        await bot.send_message(chat_id, "А ты не волонтёр!\nЖди приглашения в основном боте:\n@rogermentalbot")
        return

    if (user['is_banned_from_volunteering']):
        amplitude.track(
            BaseEvent(
                event_type="Rate message error",
                user_id=user_id,
                event_properties={
                    "user": user_to_string(user),
                    "error": {
                        "message": "User banned from volunteering"
                    }
                }
            )
        )
        await bot.send_message(chat_id, "Сообщений на оценку не осталось, возвращайся завтра 👋")
        return

    count_messages = list(
        user_messages.get_already_sended_messages(ObjectId(user['_id'])))

    if (len(count_messages) != 0):
        settings = app_settings.get_app_settings()

        if (count_messages[0]['count_messages'] >= settings['volunteer_messages_in_day']):
            amplitude.track(
                BaseEvent(
                    event_type="Rate message - no more messages",
                    user_id=user_id,
                    event_properties={
                        "user": user_to_string(user)
                    }
                )
            )
            await bot.send_message(chat_id, "Сообщений на оценку не осталось, возвращайся завтра 👋")
            return

    await get_message_and_send(user, chat_id)


async def get_message_and_send(user, chat_id):
    bot = Bot().get_bot()
    user_messages = User_Messages()
    messages = Messages()
    amplitude = Amplitude().get_amplitude()

    user_id = ObjectId(user['_id'])

    message_to_rate = messages.get_unapproved_by_user(user_id)

    message_list = list(message_to_rate)

    if (len(message_list) != 0):
        old_messages = user_messages.get_not_rated_massages(user_id)

        for old_message in old_messages:
            await delete_keyboard(chat_id, old_message['id_tg_message'])

        message_to_send = message_list[0]

        print('Отправляю сообщение: ' + str(message_to_send))

        amplitude.track(
            BaseEvent(
                event_type="Sending message to rate",
                user_id=str(user_id),
                event_properties={
                    "user": user_to_string(user),
                    "message": message_to_string(message_to_send)
                }
            )
        )

        tg_message_id = await send_message(chat_id, message_to_send)

        user_messages.insert_user_message(user_id, ObjectId(
            str(message_to_send['_id'])), tg_message_id)
    else:
        amplitude.track(
            BaseEvent(
                event_type="Rate message - no more messages",
                user_id=str(user_id),
                event_properties={
                    "user": user_to_string(user),
                }
            )
        )
        await bot.send_message(chat_id, "Сообщений на оценку не осталось, возвращайся завтра 👋")
