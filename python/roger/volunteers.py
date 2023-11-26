"""Module providing functions for volunteer interactions."""

from db.users import get_user_by_telegram_id, update_user_is_volunteer
from db.mental_rate import get_all_mental_rates
from variables import botClient


async def is_mental_rate_threashhold_reached(chat_id: int, action: str):
    """
    Function to check if user reached required threashold in mental rates

    Parameters:
    chat_id (int): Telegram ID of user
    action (str): action to check threashold, can be:
        "returnvolunteer" - 7 days
        "volunteer" - 7 days
        "stata" - 7 days
        "mantalstata" - 14 days

    Returns:
    None
    """

    amount = how_many_days_user_with_us(chat_id)

    if action == 'returnvolunteer' and amount >= 7:
        user = get_user_by_telegram_id(chat_id)
        update_user_is_volunteer(user['_id'], True)
        return True

    if action == 'volunteer' and amount == 7:
        user = get_user_by_telegram_id(chat_id)
        await botClient.send_message(
            chat_id,
            (
                "Ты дружишь со мной уже давно! "
                "Как насчет помочь мне с оценкой сообщений пользователей? \n\n"
                "Переходи в бота для волонтеров @JimmyVolunteerBot и нажимай /start"
            )
        )
        update_user_is_volunteer(user['_id'], True)
        return True

    if action == 'stata':
        return amount >= 7

    if action == 'mantalstata':
        return amount >= 14


async def how_many_days_user_with_us(chat_id: int):
    """
    Function to get number of mental rates by User

    Parameters:
    chat_id (int): Telegram ID of user

    Returns:
    int
    """

    user = get_user_by_telegram_id(str(chat_id))
    all_rates = get_all_mental_rates(user['_id'])

    return len(all_rates)
