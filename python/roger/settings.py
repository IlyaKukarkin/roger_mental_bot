from variables import botClient

from db.users import (
    update_user_name,
    update_user_timezone,
    update_user_time_to_send_messages
)
from aiogram import types
from keyboards import settings_keyboard, ask_for_name_kb
from states import Registration
from common import delete_keyboard


async def settings_main(
      tg_user_id: int  
):
    await botClient.send_message(tg_user_id,
                                    "Что хочешь изменить в своем профиле?", reply_markup = settings_keyboard)

