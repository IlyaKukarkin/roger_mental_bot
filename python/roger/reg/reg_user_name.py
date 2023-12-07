import time
from aiogram import types, dispatcher
from states import Registration
from bson import ObjectId
from db.users import update_user_name

from common import delete_keyboard
from variables import botClient, botDispatcher

# получить дефолтное имя пользователя


async def get_user_name(user_id: ObjectId, callback_query: types.CallbackQuery):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await botClient.answer_callback_query(callback_query.id)
    await botClient.send_message(callback_query.from_user.id, 'Приятно познакомиться, ' + callback_query.from_user.first_name + '!')
    update_user_name(user_id, callback_query.from_user.first_name)

# получить имя пользователя, введенное руками


async def get_printed_user_name(user_id: ObjectId, callback_query: types.CallbackQuery, source: str):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await botClient.answer_callback_query(callback_query.id)
    await botClient.send_message(callback_query.from_user.id, 'Введи свое имя ниже')
    await Registration.AwaitForAName.set()
    state = botDispatcher.get_current().current_state()
    await state.update_data(user_id=user_id, source=source)


async def get_customer_name(user_id: ObjectId, message: types.Message, state: dispatcher.FSMContext, source: str):
    await state.update_data(name=message.text)
    user_name = message.text[:80]
    if (user_name.isalpha()):
        if source == "reg":
            await botClient.send_message(message.chat.id, "Приятно познакомиться, " + user_name + "!")
        else: 
            await botClient.send_message(message.chat.id, "Записал твое новое имя, " + user_name)
        await state.finish()
        update_user_name(user_id, user_name)
        return user_name
    else:
        await botClient.send_message(message.chat.id, "Ты ошибся со вводом. Ты же не ЛСДУЗ или ЙФЯУ9? \nВведи свое имя еще раз")
        await Registration.AwaitForAName.set()
        state = botDispatcher.get_current().current_state()
        await state.update_data(user_id=user_id)
        return
