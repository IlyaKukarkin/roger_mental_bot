from datetime import datetime
import pytz

from singleton import SingletonClass


class User_Messages(object):
    def __init__(self):
        user_messages = SingletonClass().collection_name["user_messages"]

        self.user_messages = user_messages

    def insert_user_message(self, user_id, message_id, tg_message_id):
        return self.user_messages.insert_one({"id_user": user_id, "id_message": message_id, "time_to_send": datetime.now(), "id_tg_message": tg_message_id})

    def get_user_message_by_id(self, id):
        return self.user_messages.find_one({"_id": id})

    def get_user_message_by_tg_id(self, id_tg_message):
        return self.user_messages.find_one({"id_tg_message": id_tg_message})

    def get_today_messages_by_user(self, user_id):
        curr_date = datetime.now(pytz.utc)

        return self.user_messages.aggregate(
            [
                {
                    '$match': {
                        'id_user': user_id,
                        'time_to_send': {
                            '$gte': datetime(curr_date.year, curr_date.month, curr_date.day, 0, 0, 0, tzinfo=pytz.utc)
                        }
                    }
                }, {
                    '$count': 'count_messages'
                }
            ]
        )

    def get_already_sended_messages(self, user_id):
        return self.user_messages.aggregate(
            [
                {
                    '$match': {
                        'id_user': user_id,
                        'time_to_send': {
                            '$gte': datetime.now(pytz.utc)
                        }
                    }
                }
            ]
        )

    def get_not_rated_massages(self, user_id):
        return self.user_messages.aggregate([
            {
                '$match': {
                    'id_user': user_id
                }
            }, {
                '$lookup': {
                    'from': 'rate',
                    'localField': 'id_message',
                    'foreignField': 'id_message',
                    'pipeline': [
                        {
                            '$match': {
                                'id_user': user_id
                            }
                        }
                    ],
                    'as': 'rates'
                }
            }, {
                '$match': {
                    'rates.0': {
                        '$exists': False
                    }
                }
            }
        ])
