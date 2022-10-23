from datetime import datetime
from singleton import SingletonClass


class Messages(object):
    def __init__(self):
        messages = SingletonClass().collection_name["messages"]

        self.messages = messages

    def get_unapproved_by_user(self, user_id):
        return self.messages.aggregate([
            {
                '$match': {
                    '$and': [
                        {
                            'is_approved': False,
                            'id_user': {
                                '$ne': user_id
                            }
                        }
                    ]
                }
            }, {
                '$lookup': {
                    'from': 'rate',
                    'localField': '_id',
                    'foreignField': 'id_message',
                    'as': 'users'
                }
            }, {
                '$lookup': {
                    'from': 'user_messages',
                    'localField': '_id',
                    'foreignField': 'id_message',
                    'as': 'sent'
                }
            }, {
                '$project': {
                    'text': 1,
                    'id_user': 1,
                    'media_link': 1,
                    'is_ approved': 1,
                    'users': '$users.id_user',
                    'sent': '$sent.id_user',
                    'image_ids': 1,
                    'is_anonymous': 1,
                    'created_date': 1
                }
            }, {
                '$match': {
                    'users': {
                        '$ne': user_id
                    },
                    'sent': {
                        '$ne': user_id
                    }
                }
            }
        ])
