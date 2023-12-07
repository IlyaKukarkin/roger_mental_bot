from aiogram import types, dispatcher

from states import Registration
from common import delete_keyboard
from bson import ObjectId
from keyboards import ask_for_time_to_send_kb
from variables import botClient, botDispatcher
from db.users import update_user_time_to_send_messages

# получить время, когда отправлять пользователю сообщения с замером настроения


async def get_user_time_to_send_messages(user_id: ObjectId, chat_id: int, source: str):
    await botClient.send_message(chat_id, "Во сколько часов мне лучше интересоваться твоим настроением?", reply_markup=ask_for_time_to_send_kb)
    await Registration.AwaitForATimeToSend.set()
    state = botDispatcher.get_current().current_state()
    await state.update_data(user_id=user_id, source=source)


async def user_time_20(user_id: ObjectId, callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    user_time = 20
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    update_user_time_to_send_messages(user_id, user_time)
    await botClient.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " часов каждый день")
    await state.finish()
    return


async def user_time_21(user_id: ObjectId, callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    user_time = 21
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    update_user_time_to_send_messages(user_id, user_time)
    await botClient.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " час каждый день")
    await state.finish()
    return 


async def user_time_22(user_id: ObjectId, callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    user_time = 22
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    update_user_time_to_send_messages(user_id, user_time)
    await botClient.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " часа каждый день")
    await state.finish()
    return 


async def user_time_23(user_id: ObjectId, callback_query: types.CallbackQuery, state: dispatcher.FSMContext):
    user_time = 23
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    update_user_time_to_send_messages(user_id, user_time)
    await botClient.send_message(callback_query.from_user.id, "Принято! Буду приходить к тебе примерно в " + str(user_time) + " чаcа каждый день")
    await state.finish()
    return 
