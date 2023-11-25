"""Module providing functions for accessing Rate table from DB."""

from datetime import datetime
from bson import ObjectId

from db.setup import dbClient


def insert_new_rate(
    id_user: ObjectId,
    id_message: ObjectId,
    rate: bool,
):
    """
    Adds a new rate record to the DataBase table "Rate"

    Parameters:
    id_user (ObjectId): User "_id" that rates the support message
    id_message (ObjectId): Support message "_id" that was rated by user
    rate (bool): rate for the support message
        "true" - rated 👍
        "false" - rated 👎

    Returns:
    None
    """

    dbClient['rate'].insert_one({
        "id_user": id_user,
        "id_message": id_message,
        "rate": rate,
        "time_to_send": datetime.now(),
    })


def get_rate_by_user_and_message(
    id_user: ObjectId,
    id_message: ObjectId,
):
    """
    Returns an rate record from the DataBase table "Rate" by user "_id" and message "_id"

    Parameters:
    id_user (ObjectId): User "_id" that rates the support message
    id_message (ObjectId): Support message "_id" that was rated by user

    Returns:
    dict: Rate or None
    """

    rate = dbClient['rate'].find_one({
        'id_user': id_user,
        "id_message": id_message
    })

    return rate


def get_all_rates_for_message(
    id_message: ObjectId,
):
    """
    Returns an list of Rates from the DataBase table "Rate" by message "_id"

    Parameters:
    id_message (ObjectId): Support message "_id" that was rated by user

    Returns:
    list: Rate
    """

    rates = dbClient['rate'].find({"id_message": id_message})

    return rates


def count_rates_for_message(
    id_message: ObjectId,
):
    """
    Returns an dict with numbers for rates from the DataBase table "Rate" by message "_id"

    Parameters:
    id_message (ObjectId): Support message "_id" that was rated by user

    Returns:
    dict: { rate_good: number, rate_bad: number }
    """

    db_aggregation = dbClient['rate'].aggregate(
        [
            {
                '$match': {
                    'id_message': id_message
                }
            }, {
                '$group': {
                    '_id': '$rate',
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ]
    )

    result = {}

    for rate in db_aggregation:
        if rate['_id']:
            result['rate_good'] = rate['count']
        else:
            result['rate_bad'] = rate['count']

    return result
