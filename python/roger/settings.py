"""Main handler of /settings command"""
import datetime

from variables import botClient
from keyboards import settings_keyboard
from sendmessage import sendmes
from db.users import get_user_by_telegram_id
from db.mental_rate import was_mental_rate_sent_today


async def settings_main(
    tg_user_id: int
):
    """
    Fuck you python linter
    This function prints message to user
    """

    await botClient.send_message(tg_user_id,
                                 "Что хочешь изменить в своем профиле?",
                                 reply_markup=settings_keyboard)


async def check_to_send_mes(tg_id: int):
    """
    This function checks if it is needed to send message to rate user's mood
    due to changing the timezone
    """

    user = get_user_by_telegram_id(str(tg_id))
    now = datetime.datetime.now()
    if (int(user["timezone"]) + now.hour >= int(user["time_to_send_messages"])) and was_mental_rate_sent_today(user["_id"]) == False:
        await sendmes(tg_id)
