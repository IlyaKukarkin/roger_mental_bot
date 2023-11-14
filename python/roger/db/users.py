"""Module providing a date time functions."""
import datetime
from bson import ObjectId

from setup import dbClient


def insert_new_user(
    tg_username: str,
    telegram_id: str,
    username: str,
    time_zone: str,
    user_time: str
):
    """
    Adds a new user record to the DataBase table "Users";

    Parameters:
    tg_username (str): username from Telegram, starts with an "@"
    telegram_id (str): telegram id of user from Telegram
    username (str): username that user filled in
    time_zone (str): time zone that user filled in
    user_time (str): time to send "Check mental" message that user filled in

    Returns:
    None
    """

    form_id = ObjectId()

    dbClient['users'].insert_one({
        "telegram_username": tg_username,
        "name": username,
        "timezone": time_zone,
        "is_volunteer": False,
        "is_banned_from_volunteering": False,
        "form_id": form_id,
        "telegram_id": telegram_id,
        "is_admin": False,
        "is_active": True,
        "created_at": datetime.datetime.now(),
        "time_to_send_messages": user_time
    })


def get_user_by_tg_username(
    tg_username: str,
):
    """
    Returns an user record from the DataBase table "Users" by his Telegram username;

    Parameters:
    tg_username (str): username from Telegram, starts with an "@"

    Returns:
    dict: User
    """

    user = dbClient['users'].find_one({"telegram_username": tg_username})

    return user


def get_user_by_id(
    _id: ObjectId,
):
    """
    Returns an user record from the DataBase table "Users" by his "_id";

    Parameters:
    _id (ObjectId): ID for the user to find

    Returns:
    dict: User
    """

    user = dbClient['users'].find_one({"_id": _id})

    return user
