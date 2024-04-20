"""Module providing common functions."""

import json
import random
from enum import IntEnum
from datetime import datetime, timedelta, timezone
import requests
from aiogram.utils.exceptions import MessageError
from bson import ObjectId

from db.mental_rate import get_hours_since_mental_rate, get_mental_rates_period
from db.users import get_user_by_id
from db.user_messages import get_latest_message_by_user
from variables import (
    botClient,
    CONTENTFUL_API_READONLY_URL,
    CONTENTFUL_ACCESS_TOKEN,
    CONTENTFUL_SPACE_ID
)
from logger import logger

# read texts from json file
with open('texts.json', encoding="utf-8") as t:
    texts = json.load(t)


async def delete_keyboard(chat_id: int, message_id: int):
    """
    Function to delete keyboard of the message

    Parameters:
    chat_id (int): Telegram chat ID with the message
    message_id (int): Message to delete keyboard of

    Returns:
    None
    """

    try:
        await botClient.edit_message_reply_markup(
            chat_id,
            message_id,
            reply_markup=None
        )
    except MessageError as error:
        logger.exception(
            "failed to delete keyboard, tg_chat_id: %s, message_id: %s, exception: %s",
            chat_id,
            message_id,
            error
        )


async def get_pictures(picture_id: str):
    """
    Function to get the image URL from "Contentful"

    Parameters:
    picture_id (int): ID of a image from Contentful

    Returns:
    string
    """

    response = requests.get(
        CONTENTFUL_API_READONLY_URL + 'spaces/' +
        CONTENTFUL_SPACE_ID + '/environments/master/assets/' +
        picture_id + '?access_token=' +
        CONTENTFUL_ACCESS_TOKEN,
        timeout=10
    )
    answer = json.loads(response.content)
    answer = answer.get("fields").get("file").get("url")
    return str(answer[2:])


def get_options(set_name: str):
    """
    Function to get list of texts for specific set from texts.json

    Parameters:
    set_name (str): Set name to get messages
        "greetings"
        "polls_questions"
        "invite_to_form"
        "fill_form"
        "sending_support"
        "gif_support"
        "green_mood_reactions"
        "yellow_mood_reactions"
        "orange_mood_reactions"
        "red_mood_reactions"
        "what_was_good_today"
        "polls_answers"
        "good_final_message"
        "bad_final_message"
        "hurry_up_message"
        "thats_it_message"
        "mental_week_stata"

    Returns:
    str
    """

    s = rand_select_obj_texts(texts.get(set_name))
    return s.get('text')


def rand_select_obj_texts(arr: list):
    """
    Function to get a random text by frequency

    Parameters:
    arr (list): List of texts

    Returns:
    dict: Text
    """

    rand_id_array = []
    for item in arr:
        for _ in range(item.get("frequency")):
            rand_id_array.append(item.get("id"))
    rand = random.randint(0, len(rand_id_array) - 1)
    return arr[rand_id_array[rand] - 1]


async def check_if_delete_mental_keyboard(user_id: ObjectId):
    """
    Function to check if weneed to delete mental keyboard

    Parameters:
    user_id (ObjectId): User ID to check

    Returns:
    None
    """

    mental_hours = get_hours_since_mental_rate(user_id)

    if mental_hours:
        if mental_hours == 3:
            user = get_user_by_id(user_id)
            await botClient.send_message(
                int(user['telegram_id']),
                get_options('hurry_up_message')
            )

        if mental_hours == 12:
            user = get_user_by_id(user_id)
            latest_message = get_latest_message_by_user(user_id)
            await delete_keyboard(
                int(user['telegram_id']),
                latest_message['id_tg_message']
            )


class Weekdays(IntEnum):
    """Class representing a Weekday enum"""

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


def today_is_the_day(day: Weekdays, timezone_offset: int) -> bool:
    """
    A function that checks whether today is a particular weekday (specified by day parameter)
    considering the timezone offset

    Parameters:
    day (Weekdays): day to check
    timezone_offset (int): timezone offset

    Returns:
    bool
    """

    return utc_date_is_the_day(datetime.now(), day, timezone_offset)


def utc_date_is_the_day(
    date: datetime,
    day: Weekdays,
    timezone_offset: int
):
    """
    A function that checks whether the supplied date is a particular weekday
    (specified by day parameter) considering the timezone;
    date parameter should be a UTC+00 date

    Parameters:
    date (datetime): date to check
    day (Weekdays): day to check
    timezone_offset (int): timezone offset

    Returns:
    bool
    """

    delta = timedelta(hours=timezone_offset)
    tz = timezone(delta)
    date_in_tz = datetime.fromtimestamp(date.timestamp(), tz)
    return date_in_tz.weekday() == day


def n_days_since_date(number_of_days: int, date: datetime) -> bool:
    """
    Function that checks, whether a number of days has passed since a certain date

    Parameters:
    number_of_days (int): number of days passed
    date (datetime): date from which to calculate days

    Returns:
    bool
    """

    now = datetime.utcnow()
    diff: timedelta = now - date
    return diff.days > number_of_days


def any_ratings_in_previous_n_days(id_user: ObjectId, n: int = 6) -> bool:
    """
    Checks whether a user has rated their at all mood for the previous n days
    (i.e. excluding the current day);

    Parameters:
    id_user (ObjectId): chat_id and user id in mongo collection
    n (int): number of days to take into account (excluding the current day);
        the search will be conducted backwards:
            from the day before the current day to (but not including)
            the day n days before that (e.g. if we do this on a sunday,
            we will search all other six days of the week starting from Saturday to Monday,
            but not including the previous Sunday

    Returns:
    bool
    """

    today = datetime.utcnow()
    period_end = datetime(
        today.year, today.month, today.day - 1, hour=23, minute=59)
    period_start = period_end - timedelta(days=n)

    past_week_ratings = get_mental_rates_period(
        id_user,
        period_start,
        period_end
    )

    return bool(past_week_ratings)


def words_formatting(x: int):
    """False - for the words like раз
    True - for the words like раза"""

    last_two_digits = x % 100

    if last_two_digits in [11, 12, 13, 14]:
        return False
    
    last_digit = x % 10
    if last_digit in [1, 5, 6, 7, 8, 9, 0]:
        return False
    return True
