from aiogram import types
import time
from bson import ObjectId

from singleton import Bot
from db.users import Users
from db.user_messages import User_Messages
from db.messages import Messages
from utils.message import send_message
from utils.keyboards import delete_keyboard


async def start_handler(message: types.Message):
    bot = Bot().get_bot()
    users = Users()

    user = users.get_user_by_telegram_id(str(message.chat.id))

    if (not user['is_volunteer']):
        await bot.send_message(message.chat.id, "А ты не волонтёр!\nЖди приглашения в основном боте:\nhttps://t.me/RogerMentalBot", disable_web_page_preview=True)
        return

    if (user['is_banned_from_volunteering']):
        await bot.send_message(message.chat.id, "Тебя забанили, :D")
        return

    await bot.send_message(message.chat.id, "Здорова волонтёрам!")
    time.sleep(1)
    await bot.send_message(message.chat.id, "В этом чате ты можешь лайкать и дизлайкать сообщения пользователей")
    time.sleep(3)
    await bot.send_message(message.chat.id, "Все сообщения должны пройти модерацию, прежде чем попасть к основным пользователям")
    time.sleep(3)
    await bot.send_message(message.chat.id, "Периодически я буду присылать тебе сообщение для прохождения модерации")
    time.sleep(3)
    await bot.send_message(message.chat.id, "Поставь под ним лайк или дизлайк")
    time.sleep(2)
    await bot.send_message(message.chat.id, "Лови сразу первое сообщение на оценку!)")
    time.sleep(4)
    await get_message_and_send(ObjectId(user['_id']), message.chat.id)


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

        user_messages.insert_user_message(user_id, ObjectId(
            str(message_to_send['_id'])), tg_message_id)
    else:
        await bot.send_message(chat_id, "Сообщений на оценку не осталось, возвращайся завтра 👋")
