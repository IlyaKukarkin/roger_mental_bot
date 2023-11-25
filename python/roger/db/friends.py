"""Module providing functions for accessing Friends table from DB."""

from datetime import datetime
from bson import ObjectId

from db.setup import dbClient


def insert_new_friends(
    from_user_id: ObjectId,
    to_user_id: ObjectId,
    status: int = 0
):
    """
    Adds a new user record to the DataBase table "Friends"

    Parameters:
    from_user_id (ObjectId): _id of user that requested friendship
    to_user_id (ObjectId): _id of user that request sent to
    status (int): status of freindship
        0 - request sent
        1 - request approved
        2 - request declined

    Returns:
    None
    """

    dbClient['friends'].insert_one({
        "from": from_user_id,
        "to": to_user_id,
        "status": status,
        "request_sent_time": datetime.now(),
    })


def update_friend_status(
    _id: ObjectId,
    status: int = 0
):
    """
    Updates the "status" field for friends record by "_id"

    Parameters:
    _id (ObjectId): ID for the friends record to update
    status (int): value for "status" to set

    Returns:
    None
    """

    dbClient['friends'].find_one_and_update(
        {'_id': _id},
        {"$set": {'status': status}}
    )


def get_frinds_record(
    from_user_id: ObjectId,
    to_user_id: ObjectId,
):
    """
    Returns a "friends" record from the DataBase table "Friends" by both freinds _id

    Parameters:
    from_user_id (ObjectId): _id of user that requested friendship
    to_user_id (ObjectId): _id of user that request sent to

    Returns:
    dict: Frineds or None
    """

    friends = dbClient['friends'].find_one({
        "from": from_user_id,
        "to": to_user_id
    })

    return friends


# Update with new Friends architecture
def get_all_friends(
    user_id: ObjectId,
):
    """
    Returns an array of "_id" friends from the DataBase table "Friends" by User "_id"

    Parameters:
    user_id (ObjectId): ID for the user to find all freinds

    Returns:
    list: ObjectId
    """

    friends_id = []

    friends_from_user = dbClient['friends'].find(
        {"from": user_id, "status": 1}
    )

    friends_to_user = dbClient['friends'].find(
        {"to": user_id, "status": 1}
    )

    for friend in friends_from_user:
        friends_id.append(friend['to'])

    for friend in friends_to_user:
        friends_id.append(friend['from'])

    return friends_id


def get_incoming_requests(
    user_id: ObjectId,
):
    """
    Returns a list of friends requests from the DataBase table "Users" by User "_id"

    Parameters:
    user_id (ObjectId): ID of user to find all requests

    Returns:
    list: ObjectId
    """

    friends_requests_id = []

    friends_to_user = dbClient['friends'].find(
        {"to": user_id, "status": 0}
    )

    for friend in friends_to_user:
        friends_requests_id.append(friend['from'])

    return friends_requests_id
