"""Module providing functions for accessing Mental Rate table from DB."""

from datetime import datetime
import pytz
from bson import ObjectId

from db.setup import dbClient


def insert_new_mental_rate(
    id_user: ObjectId,
    rate: int,
    id_tg_message: ObjectId,
):
    """
    Adds a new mental rate record to the DataBase table "mental_rate"

    Parameters:
    id_user (ObjectId): ID of an User that has rated the mental state
    rate (int): rate number
        0 - user hasn't rated the mental state
        1 - red mental rate
        2 - orange mental rate
        3 - yellow mental rate
        4 - green mental rate
    id_tg_message (ObjectId): ID of the message that has the mental rate keyboard

    Returns:
    None
    """

    dbClient["mental_rate"].insert_one({
        "rate": rate,
        "id_user": id_user,
        "date": datetime.now(),
        "id_tg_message": id_tg_message
    })


def get_mental_rate_by_user_and_tg_message(
    id_user: ObjectId,
    id_tg_message: ObjectId,
):
    """
    Gets a mental rate record from the DataBase table "mental_rate" by "id_user" and "tg_message"

    Parameters:
    id_user (ObjectId): ID of an User that has rated the mental state
    id_tg_message (ObjectId): ID of the message that has the mental rate keyboard

    Returns:
    dict: Mental Rate
    """

    mental_rate = dbClient["mental_rate"].find_one({
        "$and": [
            {"id_user": id_user},
            {"id_tg_message": id_tg_message}
        ]
    })

    return mental_rate


def get_unrated_mental_rate(
    id_user: ObjectId,
):
    """
    Gets a mental rate record with rate "0" for the user

    Parameters:
    id_user (ObjectId): ID of an User that has rated the mental state

    Returns:
    None or dict: Mental Rate
    """

    mental_rate = dbClient["mental_rate"].find_one(
        {
            "rate": 0,
            "id_user": id_user
        },
        sort=[("date", -1)])

    return mental_rate


def get_all_mental_rates(
    id_user: ObjectId,
):
    """
    Gets all mental rates record with rate "1" or higher for the user

    Parameters:
    id_user (ObjectId): ID of an User that has rated the mental state

    Returns:
    list: Mental Rate
    """

    mental_rates = dbClient["mental_rate"].find(
        {
            "$and": [
                {"id_user": id_user},
                {"rate": {"$gt": 0}}
            ]
        },
        sort=[("date", -1)])

    return list(mental_rates)


def get_mental_rates_period(
    id_user: ObjectId,
    period_start: datetime,
    period_end: datetime,
):
    """
    Gets all mental rates record with rate "1" or higher for the user

    Parameters:
    id_user (ObjectId): ID of an User to get mental rates
    period_start (datetime): start of period
    period_end (datetime): end of period

    Returns:
    list: Mental Rate
    """

    mental_rates = dbClient["mental_rate"].find({
        'id_user': id_user,
        'date': {'$gt': period_start, '$lt': period_end},
        'rate': {'$gt': 0}
    })

    return list(mental_rates)


def update_mental_rate_value(
    _id: ObjectId,
    rate: int,
):
    """
    Updates a "Rate" value for a mental rate record in the DataBase table "mental_rate"

    Parameters:
    _id (ObjectId): ID of the record to update
    rate (int): rate number
        0 - user hasn't rated the mental state
        1 - red mental rate
        2 - orange mental rate
        3 - yellow mental rate
        4 - green mental rate

    Returns:
    None
    """

    dbClient["mental_rate"].find_one_and_update(
        {"_id": _id},
        {"$set": {"rate": rate}}
    )


def was_mental_rate_sent_today(
    id_user: ObjectId,
):
    """
    Returns a boolean value if Mental Rate was already asked for the user today

    Parameters:
    id_user (ObjectId): ID user to search mental rates

    Returns:
    boolean
    """

    curr_date = datetime.now(pytz.utc)

    mental_rates = dbClient["mental_rate"].find({
        'id_user': id_user,
        'date': {
            '$gte': datetime(
                curr_date.year,
                curr_date.month,
                curr_date.day,
                0,
                0,
                0,
                tzinfo=pytz.utc
            )
        }
    })

    return bool(list(mental_rates))


def get_hours_since_mental_rate(
    id_user: ObjectId,
):
    """
    Returns a int value with number of hours passed since message with "Mental Rate" was send

    Parameters:
    id_user (ObjectId): ID user to search mental rates

    Returns:
    int
    """

    hours_passed = dbClient["mental_rate"].aggregate(
        [
            {
                '$match': {
                    'id_user': id_user,
                    'rate': 0
                }
            }, {
                '$addFields': {
                    'datetime_now': datetime.now(pytz.utc)
                }
            }, {
                '$addFields': {
                    'date_diff': {
                        '$dateDiff': {
                            'startDate': '$date',
                            'endDate': '$datetime_now',
                            'unit': 'hour'
                        }
                    }
                }
            }, {
                '$sort': {
                    'date_diff': 1
                }
            }, {
                '$limit': 1
            }
        ])

    if hours_passed is None:
        return 0

    return list(hours_passed)[0]
