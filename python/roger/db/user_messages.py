"""Module providing functions for accessing User Messages table from DB."""

from datetime import datetime
from bson import ObjectId

from db.setup import dbClient


def insert_new_user_message(
    id_user: ObjectId,
    id_message: ObjectId,
    id_tg_message: str,
):
    """
    Adds a new user message record to the DataBase table "User messages"

    Parameters:
    id_user (ObjectId): username from Telegram, starts with an "@"
    id_message (ObjectId): telegram id of user from Telegram
    id_tg_message (int): time zone that user filled in

    Returns:
    None
    """

    dbClient['user_messages'].insert_one({
        "id_user": id_user,
        "id_message": id_message,
        "time_to_send": datetime.now(),
        "id_tg_message": id_tg_message
    })


def get_user_message_by_tg_message(
    id_tg_message: int,
):
    """
    Returns an user message record from the DataBase table "User messages" by id_tg_message

    Parameters:
    id_tg_message (int): ID of this message in Bot chat of the user

    Returns:
    dict: User message
    """

    user_message = dbClient['user_messages'].find_one({
        "id_tg_message": id_tg_message
    })

    return user_message


def get_latest_message_by_user(
    id_user: ObjectId,
):
    """
    Returns an user message record from the DataBase table "User messages" by user "_id"

    Parameters:
    id_user (ObjectId): ID of user to find latest message

    Returns:
    dict: User message
    """

    user_message = dbClient['user_messages'].find_one(
        {"id_user": id_user},
        sort=[("time_to_send", -1)]
    )

    return user_message


def get_message_by_message_id(
    id_message: ObjectId,
):
    """
    Returns an user message record from the DataBase table "User messages" by message "_id"

    Parameters:
    id_message (ObjectId): ID of message that was sent to user

    Returns:
    dict: User message
    """

    user_message = dbClient['user_messages'].find_one(
        {"id_message": id_message})

    return user_message


def get_all_messages_by_message_id(
    id_message: ObjectId,
):
    """
    Returns all user message records from the DataBase table "User messages" by message "_id"

    Parameters:
    id_message (ObjectId): ID of message that was sent to user

    Returns:
    list: User message
    """

    user_messages = dbClient['user_messages'].find(
        {"id_message": id_message})

    return list(user_messages)
