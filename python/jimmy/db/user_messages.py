from datetime import datetime

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
