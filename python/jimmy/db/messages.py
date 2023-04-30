from singleton import SingletonClass


class Messages(object):
    def __init__(self):
        messages = SingletonClass().collection_name["messages"]

        self.messages = messages

    def get_all(self):
        return self.messages.find()

    def update_message(self, id, media_link, original_media_link):
        return  self.messages.update_one({'_id': id}, { "$set": { 'media_link': media_link, 'original_media_link': original_media_link } })
    
    def get_unapproved_by_user(self, user_id):
        return self.messages.aggregate([
            {
                '$match': {
                    '$and': [
                        {
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
                    'created_date': 1, 
                    'rates_count': {
                        '$size': '$users'
                }
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
            }, {
                '$sort': {
                    'rates_count': 1
                }
            }, {
                '$limit': 10
            }
])
