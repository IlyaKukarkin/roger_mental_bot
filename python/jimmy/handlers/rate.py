from aiogram import types
from bson import ObjectId

from singleton import Bot
from db.users import Users
from db.rate import Rate
from db.app_settings import App_Settings
from db.user_messages import User_Messages
from db.messages import Messages
from utils.message import send_message
from utils.keyboards import delete_keyboard

async def rate_handler(message: types.Message):
    bot = Bot().get_bot()
    users = Users()
    user_messages = User_Messages()
    app_settings = App_Settings()

    user = users.get_user_by_telegram_id(str(message.chat.id))
    user_id = ObjectId(user['_id'])

    if (not user['is_volunteer']):
        await bot.send_message(message.chat.id, "А ты не волонтёр!\nЖди приглашения в основном боте:\nhttps://t.me/RogerMentalBot")
        return

    if (user['is_banned_from_volunteering']):
        await bot.send_message(message.chat.id, "Тебя забанили, :D")
        return

    count_messages = list(user_messages.get_today_messages_by_user(user_id))

    if (len(count_messages) != 0):
        settings = app_settings.get_app_settings()

        if (count_messages[0]['count_messages'] >= settings['volunteer_messages_in_day']):
            await bot.send_message(message.chat.id, "Сообщений на оценку не осталось, возвращайся завтра 👋")
            return

    await get_message_and_send(user_id, message.chat.id)

async def get_message_and_send(user_id, chat_id):
    bot = Bot().get_bot()
    user_messages = User_Messages()
    messages = Messages()

    message_to_rate = messages.get_unapproved_by_user(user_id)

    message_list = list(message_to_rate)

    if (len(message_list) != 0):
        old_messages = user_messages.get_not_rated_massages(user_id)
        
        for old_message in old_messages:
            await delete_keyboard(chat_id, old_message['id_tg_message'])

        message_to_send = message_list[0]

        print('Отправляю сообщение: ' + str(message_to_send))

        await bot.send_message(chat_id, "Оцени пожалуйста это сообщение от пользователя:")

        tg_message_id = await send_message(chat_id, message_to_send)
        
        user_messages.insert_user_message(user_id, ObjectId(str(message_to_send['_id'])), tg_message_id)
    else:
        await bot.send_message(chat_id, "Сообщений на оценку не осталось, возвращайся завтра 👋")
