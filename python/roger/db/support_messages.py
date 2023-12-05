"""Module providing functions for accessing Support Messages Income/Outcome table from DB."""

from datetime import datetime
from bson import ObjectId

from db.setup import dbClient


# Merge two tables into one


def insert_income_support_message(
    user_id: ObjectId,
    tg_id_user: int,
    id_tg_message: int,
    text: str,
):
    """
    Adds a new income support message record to the DataBase table "Support messages income"

    Parameters:
    user_id (ObjectId): user "_id" from DataBase
    tg_id_user (int): telegram ID of user from Telegram
    id_tg_message (int): message ID from Telegram
    text (str): text that was sent

    Returns:
    None
    """

    dbClient['support_messages_income'].insert_one({
        "user_id": user_id,
        "tg_id_user": tg_id_user,
        "time_to_send": datetime.now(),
        "id_tg_message": id_tg_message,
        "text": text
    })


def insert_outcome_support_message(
    user_id: ObjectId,
    tg_id_user: int,
    id_tg_message: int,
    text: str,
):
    """
    Adds a new outcome support message record to the DataBase table "Support messages outcome"

    Parameters:
    user_id (ObjectId): user "_id" from DataBase
    tg_id_user (int): telegram ID of user from Telegram
    id_tg_message (int): message ID from Telegram
    text (str): text that was sent

    Returns:
    None
    """

    dbClient['support_messages_outcome'].insert_one({
        "user_id": user_id,
        "tg_id_user": tg_id_user,
        "time_to_send": datetime.now(),
        "id_tg_message": id_tg_message,
        "text": text,
        "rate": None
    })


def update_outcome_message_rate(
    tg_id_user: int,
    id_tg_message: int,
    rate: bool,
):
    """
    Updates a outcome message record from the DataBase table "Support messages outcome"
    by user ID from Telegram and message ID

    Parameters:
    tg_id_user (int): telegram ID of user from Telegram
    id_tg_message (int): message ID from Telegram
    rate (bool): rate for Bot message (true/false)

    Returns:
    None
    """

    dbClient['support_messages_outcome'].find_one_and_update(
        {
            'tg_id_user': tg_id_user,
            "id_tg_message": id_tg_message
        },
        {"$set": {'rate': rate}}
    )
