from aiogram import types
from aiogram.dispatcher import FSMContext

from states import Registration
from common import delete_keyboard
from keyboards import ask_for_time_to_send_kb
from config import bot

#получить время, когда отправлять пользователю сообщения с замером настроения
async def get_user_time_to_send_messages(chat_id: int):
    await bot.send_message(chat_id, "Во сколько часов мне лучше интересоваться твоим настроением?", reply_markup=ask_for_time_to_send_kb)
    await Registration.AwaitForATimeToSend.set()

async def user_time_20(callback_query: types.CallbackQuery, state: FSMContext):
    user_time = 20
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " часов каждый день")
    await state.finish()
    return user_time


async def user_time_21(callback_query: types.CallbackQuery, state: FSMContext):
    user_time = 21
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " час каждый день")
    await state.finish()
    return user_time


async def user_time_22(callback_query: types.CallbackQuery, state: FSMContext):
    user_time = 22
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " часа каждый день")
    await state.finish()
    return user_time


async def user_time_23(callback_query: types.CallbackQuery, state: FSMContext):
    user_time = 23
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " чаcа каждый день")
    await state.finish()
    return user_time

