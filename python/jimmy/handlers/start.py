from aiogram import types
import time

from singleton import Bot
from db.users import Users

async def start_handler(message: types.Message):
    bot = Bot().get_bot()
    users = Users()

    user = users.get_user_by_telegram_id(str(message.chat.id))

    if (not user['is_volunteer']):
        await bot.send_message(message.chat.id, "А ты не волонтёр!\nЖди приглашения в основном боте:\nhttps://t.me/roger_mental_bot")
        return

    if (user['is_banned_from_volunteering']):
        await bot.send_message(message.chat.id, "Тебя забанили, :D")
        return

    await bot.send_message(message.chat.id, "Здорова волонтёрам!")
    time.sleep(1)
    await bot.send_message(message.chat.id, "В этом чате ты можешь лайкать и дизлайкать сообщения пользователей")
    time.sleep(2)
    await bot.send_message(message.chat.id, "Все сообщения должны пройти модерацию, прежде чем попасть к основным пользователям")
    time.sleep(3)
    await bot.send_message(message.chat.id, "Периодически, мы будем присылать тебе сообщение для прохождения модерации")
    time.sleep(3)
    await bot.send_message(message.chat.id, "Поставь под ним лайк или дизлайк")
