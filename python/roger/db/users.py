"""Module providing functions for accessing Users table from DB."""

from datetime import datetime
from bson import ObjectId

from db.setup import dbClient


def insert_new_user(
    tg_username: str,
    telegram_id: str,
    username: str,
    time_zone: str,
    user_time: str,
    form_id: ObjectId
):
    """
    Adds a new user record to the DataBase table "Users"

    Parameters:
    tg_username (str): username from Telegram, starts with an "@"
    telegram_id (str): telegram id of user from Telegram
    username (str): username that user filled in
    time_zone (str): time zone that user filled in
    user_time (str): time to send "Check mental" message that user filled in

    Returns:
    None
    """

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
        "created_at": datetime.now(),
        "time_to_send_messages": user_time
    })


def update_user_is_active(
    _id: ObjectId,
    is_active: bool
):
    """
    Updates the "is_active" field for user by his "_id"

    Parameters:
    _id (ObjectId): ID for the user to update
    is_active (bool): value for "is_active" to set

    Returns:
    None
    """

    dbClient['users'].find_one_and_update(
        {'_id': _id}, {"$set": {'is_active': is_active}})


def update_user_is_volunteer(
    _id: ObjectId,
    is_volunteer: bool
):
    """
    Updates the "is_volunteer" field for user by his "_id"

    Parameters:
    _id (ObjectId): ID for the user to update
    is_volunteer (bool): value for "is_volunteer" to set

    Returns:
    None
    """

    dbClient['users'].find_one_and_update(
        {'_id': _id}, {"$set": {'is_volunteer': is_volunteer}})


def get_user_by_tg_username(
    tg_username: str,
):
    """
    Returns an user record from the DataBase table "Users" by his Telegram username

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
    Returns an user record from the DataBase table "Users" by his "_id"

    Parameters:
    _id (ObjectId): ID for the user to find

    Returns:
    dict: User
    """

    user = dbClient['users'].find_one({"_id": _id})

    return user


def get_user_by_telegram_id(
    telegram_id: str,
):
    """
    Returns an user record from the DataBase table "Users" by his "telegram_id"

    Parameters:
    telegram_id (str): Telegram ID for the user to find

    Returns:
    dict: User
    """

    user = dbClient['users'].find_one({"telegram_id": telegram_id})

    return user


def get_all_admins():
    """
    Returns an array of all admin users from the DataBase table "Users"

    Parameters:

    Returns:
    array: Users
    """

    admin_users = dbClient['users'].find({"is_admin": True, "is_active": True})

    return admin_users


def get_all_active_users():
    """
    Returns an array of all active users from the DataBase table "Users"

    Parameters:

    Returns:
    array: Users
    """

    all_users = dbClient['users'].find({"is_active": True})

    return all_users


def get_user_with_mental_rate(
    _id: ObjectId,
    from_date: datetime
):
    """
    Returns an user by "_id" with all mental rates from specific date

    Parameters:
    _id (ObjectId): ID for the user to find
    from_date (datetime): date from which aggregate "mental_rate"

    Returns:
    dict: User
        rates: array of "Mental Rate"
    """

    user = dbClient['users'].aggregate(
        [
            {
                '$match': {
                    '_id': _id
                }
            }, {
                '$lookup': {
                    'from': 'mental_rate',
                    'localField': '_id',
                    'foreignField': 'id_user',
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$gte': [
                                        '$date', from_date
                                    ]
                                }
                            }
                        }
                    ],
                    'as': 'rates'
                }
            }
        ]
    )

    return list(user)[0]
