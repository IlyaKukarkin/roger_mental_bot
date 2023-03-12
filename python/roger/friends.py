from aiogram import types
from config import bot
from database import get_database, search_user_by_nickname, send_friends_request
from states import Recording
from aiogram.dispatcher import FSMContext


async def await_for_a_friend_nickname(message: types.Message):
    await bot.send_message(message.chat.id, "Введи ник своего друга в Telegram, а я проверю, знаком ли я с ним 🙃")
    await Recording.AwaitForAFriendNicknameToAdd.set()

async def get_friend_nickname(message: types.Message, state: FSMContext):
    if message.text == "/stop":
        await state.finish()
        await bot.send_message(message.chat.id, "Ты вышел из режима ввода")
        return 
    
    if str(message.text)[0] == '/':
        await bot.send_message(message.chat.id, "Ты находишься в режиме ввода никнейма друга. Чтобы выйти из него, выбери команду /stop, а затем повторно вызови нужную команду")
        await Recording.AwaitForAFriendNicknameToAdd.set()
        return

    if str(message.text)[0] != '@':
        message.text = "@" + message.text
    
    if message.text == '@':
        await bot.send_message(message.chat.id, "Это ник Павла Дурова? Перепроверь и введи корректный ник еще раз 🙃")
        await Recording.AwaitForAFriendNicknameToAdd.set()
        return
    
    friend = await search_user_by_nickname(message.text, message.chat.id)

    if (friend == None):
        await bot.send_message(message.chat.id, "Я не знаю этого челика")
        await Recording.AwaitForAFriendNicknameToAdd.set()

    else: 
        await send_friends_request(message.chat.id, friend)
        await bot.send_message(message.chat.id, "Отправил запрос дружбы пользователю " + message.text)

#пока не работает 



    
