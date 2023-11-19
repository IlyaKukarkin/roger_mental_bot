"""Module providing functions for accessing Messages table from DB."""

from bson import ObjectId

from db.setup import dbClient


def get_message_by_id(
    _id: ObjectId,
):
    """
    Returns an message record from the DataBase table "Message" by "_id"

    Parameters:
    _id (ObjectId): ID for the message to find

    Returns:
    dict: Message
    """

    message = dbClient["messages"].find_one(
        {"_id": _id})

    return message


def get_all_messages_by_user(
    id_user: ObjectId,
):
    """
    Returns array of messages by created User

    Parameters:
    id_user (ObjectId): ID of user to find all messages

    Returns:
    array: Messages
    """

    messages = dbClient['messages'].find({"id_user": id_user})

    return messages


def get_message_to_send_to_user(
    id_user: ObjectId,
):
    """
    Returns an message record from the DataBase table "Message" for user to send
    Includes only:
        Approved messages
        Not created by this user
        Not alredy sended before

    Parameters:
    id_user (ObjectId): ID of user to send support message

    Returns:
    dict: Message
    """

    message = dbClient["messages"].aggregate([
        {
            '$match': {
                'is_approved': True,
                'id_user': {
                    '$ne': id_user
                }
            }
        }, {
            '$lookup': {
                'from': 'user_messages',
                'localField': 'id_message',
                'foreignField': '_id',
                'pipeline': [
                    {
                        '$match': {
                            'id_user': id_user
                        }
                    }
                ],
                'as': 'sended'
            }
        }, {
            '$match': {
                'sended': {
                    '$not': {
                        '$size': 1
                    }
                }
            }
        }, {
            '$sample': {
                'size': 1
            }
        }, {
            '$lookup': {
                'from': 'users',
                'localField': 'id_user',
                'foreignField': '_id',
                'as': 'user'
            }
        }
    ])

    return message
