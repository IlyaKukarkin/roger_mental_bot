"""Module providing functions for accessing Friends table from DB."""

from datetime import datetime
from bson import ObjectId

from db.setup import dbClient


def insert_new_friends(
    from_user_id: ObjectId,
    to_user_id: ObjectId
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

    dbClient['friends_requests'].insert_one({
        "from": from_user_id,
        "to": to_user_id,
        "request_sent_time": datetime.now(),
    })


def get_friends_record(
    from_user_id: ObjectId,
    to_user_id: ObjectId,
):
    """
    Returns a "friends" record from the DataBase table "Friends" by both freinds _id

    Parameters:
    from_user_id (ObjectId): _id of user that requested friendship
    to_user_id (ObjectId): _id of user that request sent to

    Returns:
    dict: Friends or None
    """

    friends = dbClient['friends_requests'].find_one({
        "from": from_user_id,
        "to": to_user_id
    })

    return friends


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

    friends_ids = dbClient['users'].find(
        {"_id": user_id}, {"_id": 0, "friends": 1}
    )
    friends_ids = list(friends_ids)

    if friends_ids[0] == {}:
        return []

    return friends_ids[0].get("friends")


def get_incoming_requests(
    user_id: ObjectId,
):
    """
    Returns a list of friends requests to this user from the DataBase table "Users" by User "_id"

    Parameters:
    user_id (ObjectId): ID of user to find all incoming requests

    Returns:
    list: ObjectId
    """

    friends_requests_id = []

    friends_to_user = dbClient['friends_requests'].find(
        {"to": user_id}
    )

    for friend in friends_to_user:
        friends_requests_id.append(friend['from'])

    return friends_requests_id


def get_outcoming_requests(
    user_id: ObjectId,
):
    """
    Returns a list of friends requests from this user from the DataBase table "Users" by User "_id"

    Parameters:
    user_id (ObjectId): ID of user to find all outcoming requests

    Returns:
    list: ObjectId
    """

    friends_requests_id = []

    friends_from_user = dbClient['friends_requests'].find(
        {"from": user_id}
    )

    for friend in friends_from_user:
        friends_requests_id.append(friend['to'])

    return friends_requests_id


def delete_friends_request(user_to: ObjectId, user_from: ObjectId):

    dbClient["friends_requests"].delete_one({'from': user_to, 'to': user_from})
    dbClient["friends_requests"].delete_one({'from': user_from, 'to': user_to})


def add_new_friend(user_to: ObjectId, user_from: ObjectId):

    friends_of_user_to = get_all_friends(user_to)
    friends_of_user_to.append(user_from)

    dbClient["users"].find_one_and_update(
        {'_id': user_to}, {"$set": {'friends': friends_of_user_to}})

    friends_of_user_from = get_all_friends(user_from)
    friends_of_user_from.append(user_to)

    dbClient["users"].find_one_and_update(
        {'_id': user_from}, {"$set": {'friends': friends_of_user_from}})


def delete_from_friends(user_to: ObjectId, user_from: ObjectId):

    friends_of_user_to = get_all_friends(user_to)
    friends_of_user_to.remove(user_from)

    dbClient["users"].find_one_and_update(
        {'_id': user_to}, {"$set": {'friends': friends_of_user_to}})

    friends_of_user_from = get_all_friends(user_from)
    friends_of_user_from.remove(user_to)

    dbClient["users"].find_one_and_update(
        {'_id': user_from}, {"$set": {'friends': friends_of_user_from}})


def count_all_user_friends_request(user: ObjectId):
    "Returns number of internal and external friends requests"

    count_requests = dbClient["friends_requests"].aggregate([
        {
            '$match': {
                '$or': [
                    {
                        'from': user["_id"]
                    }, {
                        'to': user["_id"]
                    }
                ]
            }
        }, {
            '$count': 'count'
        }
    ]
    )
    count_requests = list(count_requests)
    if not count_requests:
        return 0
    return count_requests[0].get("count")
