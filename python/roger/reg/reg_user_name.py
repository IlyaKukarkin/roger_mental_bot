from aiogram import types

from states import Registration
from aiogram.dispatcher import FSMContext
import time

from common import delete_keyboard
from config import bot

#получить дефолтное имя пользователя
async def get_user_name(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)
    user_name = callback_query.from_user.first_name
    await bot.send_message(callback_query.from_user.id, 'Приятно познакомиться, ' + user_name + '!')
    time.sleep(1)
    await state.finish()
    return user_name

#получить имя пользователя, введенное руками
async def get_printed_user_name(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Введи свое имя ниже')
    await Registration.AwaitForAName.set()

async def get_customer_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    user_name = message.text[:80]
    if (user_name.isalpha()):
        await bot.send_message(message.chat.id, "Приятно познакомиться, " + user_name + "!")
        await state.finish()
        return user_name
    else:
        await bot.send_message(message.chat.id, "Ты ошибся со вводом. Ты же не ЛСДУЗ или ЙФЯУ9? \nВведи свое имя еще раз")
        await Registration.AwaitForAName.set()
        return