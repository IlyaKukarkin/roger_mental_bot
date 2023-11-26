"""Module providing functions for getting statistic for mental rates."""

from datetime import datetime
import urllib.parse
from typing import Callable
import json
import pytz
from dateutil.relativedelta import relativedelta
from aiogram import types

from variables import botClient
from states import Recording
from keyboards import ask_for_rate_stata_kb
from volunteers import is_mental_rate_threashhold_reached
from db.users import get_user_by_telegram_id
from db.mental_rate import get_mental_rates_period
from db.statistic import get_statistic


async def get_rate_stata(message: types.Message):
    """
    Message handler for /mentalstata command

    Parameters:
    message (TG Message): message to handle

    Returns:
    None
    """

    is_command_allowed = await is_mental_rate_threashhold_reached(message.chat.id, 'mantalstata')

    if not is_command_allowed:
        await botClient.send_message(
            message.chat.id,
            "Эта команда тебе пока недоступна. Замеряй свое настроение 14 дней — и она откроется!"
        )
        return

    await botClient.send_message(
        message.chat.id,
        "За какой период хочешь получить статистику?",
        reply_markup=ask_for_rate_stata_kb
    )
    await Recording.AwaitForARateStata.set()


async def send_rate_stata(
    id_tg_user: int,
    stata_type: str,
    datetime_factory: Callable[
        [pytz.BaseTzInfo], datetime] = datetime.now
):
    """
    Callback handler for /mentalstata command

    Parameters:
    id_tg_user (int): Telegram ID of user
    stata_type (str): Type of statistic to show, can be:
        "month"
        "week2"
        "week"
    datetime_factory (Callable ?? <- some advanced Python, I don't understand it):
        a factory method, that produces a date which will be used as the end of the period

    Returns:
    None
    """

    await botClient.send_message(str(id_tg_user), "Подгружаю статистику, немного терпения")

    date_from, date_to = get_date_range(stata_type, datetime_factory)

    user = get_user_by_telegram_id(str(id_tg_user))
    rates = get_mental_rates_period(
        user['_id'],
        date_from,
        date_to
    )

    data = []
    count_rates = 0

    for i in range(0, date_from.weekday()):
        data.append(
            {"date": i, "mood": 0, "disabled": True}
        )

    for dt in daterange(date_from.date(), date_to.date()):
        for index, rate in rates:
            if rate['date'].date() == dt:
                if rate["rate"] != 0:
                    count_rates += 1

                data.append(
                    {"date": dt.day, "mood": rate["rate"], "disabled": False}
                )
                break

            if index == len(user['rates']) - 1:
                data.append(
                    {"date": dt.day, "mood": 0, "disabled": dt <
                        user['created_at'].date()}
                )

    image_url_params = (
        "?username=" + urllib.parse.quote(user['name']) +
        "&compare_to_others=" + get_statistic_data(stata_type, count_rates) +
        "&title=" + urllib.parse.quote(
            f"с {date_from.strftime('%d.%m.%Y')} по {date_to.strftime('%d.%m.%Y')}"
        ) +
        "&data=" + urllib.parse.quote(json.dumps(data))
    )

    image_url = 'https://rogerbot.tech/api/user-stats' + image_url_params

    await botClient.send_photo(id_tg_user, image_url)


def get_date_range(
    stata_type: str,
    datetime_factory: Callable[
        [pytz.BaseTzInfo], datetime] = datetime.now
):
    """
    Function to get Date range for statistic

    Parameters:
    stata_type (str): Type of statistic to show, can be:
        "month"
        "week2"
        "week"
    datetime_factory (Callable ?? <- some advanced Python, I don't understand it):
        a factory method, that produces a date which will be used as the end of the period

    Returns:
    [date_from, date_to]
    """
    date_now = datetime_factory(pytz.utc)
    date_now_clear = datetime(
        date_now.year, date_now.month, date_now.day, 0, 0, 0, 0, tzinfo=pytz.utc)

    if stata_type == 'month':
        from_date_str = date_now_clear - \
            relativedelta(months=1) + relativedelta(days=1)
    elif stata_type == 'week2':
        from_date_str = date_now_clear - relativedelta(days=13)
    else:
        from_date_str = date_now_clear - relativedelta(days=6)

    from_date = datetime.strptime(
        str(from_date_str), '%Y-%m-%d %H:%M:%S%z')

    return [from_date, date_now_clear]


def get_statistic_data(
    stata_type: str,
    count_rates: int
):
    """
    Function to get statistic of User compared to other users

    Parameters:
    stata_type (str): Type of statistic to show, can be:
        "month"
        "week2"
        "week"
    count_rates (int): number of mental rates of User to compare

    Returns:
    int
    """

    statistic = get_statistic()

    compare = 0
    compare_total_users = 0

    if stata_type == 'month':
        compare_total_users = len(statistic["users_rate_month"])
        for other_user_rates in statistic["users_rate_month"]:
            if count_rates > other_user_rates:
                compare += 1
    elif stata_type == 'week2':
        compare_total_users = len(statistic["users_rate_2week"])
        for other_user_rates in statistic["users_rate_2week"]:
            if count_rates > other_user_rates:
                compare += 1
    else:
        compare_total_users = len(statistic["users_rate_week"])
        for other_user_rates in statistic["users_rate_week"]:
            if count_rates > other_user_rates:
                compare += 1

    return round(compare / compare_total_users * 100)


def daterange(
    date_start: datetime,
    date_end: datetime
):
    """
    Function to generate array of dates from date range

    Parameters:
    date_start (datetime): Date start range
    date_end (datetime): Date end range

    Returns:
    list of datetime
    """

    for n in range(int((date_end - date_start).days) + 1):
        yield date_start + datetime.timedelta(n)
