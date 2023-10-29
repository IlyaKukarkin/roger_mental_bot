from datetime import datetime
import pytz

from singleton import SingletonClass


class Users(object):
    def __init__(self):
        users = SingletonClass().collection_name["users"]

        self.users = users

    def get_all_volunteers_by_time(self):
        currDate = datetime.now(pytz.utc)

        return self.users.aggregate([
            {
                '$match': {
                    'is_volunteer': True,
                    'is_active': True,
                    'is_banned_from_volunteering': False
                }
            }, {
                '$project': {
                    'is_banned_from_volunteering': 1,
                    'form_id': 1,
                    'telegram_id': 1,
                    'created_at': 1,
                    'name': 1,
                    'timezone': {
                        '$toDouble': '$timezone'
                    },
                    'is_volunteer': 1,
                    'is_active': 1,
                    'telegram_username': 1,
                    'is_admin': 1,
                    'time_to_send_messages': 1,
                    'hour_now': {
                        '$hour': currDate
                    }
                }
            }, {
                '$project': {
                    'is_banned_from_volunteering': 1,
                    'form_id': 1,
                    'telegram_id': 1,
                    'created_at': 1,
                    'name': 1,
                    'timezone': 1,
                    'is_volunteer': 1,
                    'is_active': 1,
                    'telegram_username': 1,
                    'is_admin': 1,
                    'time_to_send_messages': 1,
                    'date_now': {
                        '$dateFromParts': {
                            'year': {
                                '$year': currDate
                            },
                            'hour': '$hour_now'
                        }
                    },
                    'date_user': {
                        '$dateFromParts': {
                            'year': {
                                '$year': currDate
                            },
                            'hour': {
                                '$add': [
                                    '$hour_now', '$timezone'
                                ]
                            }
                        }
                    }
                }
            }, {
                '$project': {
                    'is_banned_from_volunteering': 1,
                    'form_id': 1,
                    'telegram_id': 1,
                    'created_at': 1,
                    'name': 1,
                    'timezone': 1,
                    'is_volunteer': 1,
                    'is_active': 1,
                    'telegram_username': 1,
                    'is_admin': 1,
                    'time_to_send_messages': 1,
                    'hour_user': {
                        '$toDouble': {
                            '$dateToString': {
                                'date': '$date_user',
                                'format': '%H'
                            }
                        }
                    }
                }
            }, {
                '$project': {
                    'is_banned_from_volunteering': 1,
                    'form_id': 1,
                    'telegram_id': 1,
                    'created_at': 1,
                    'name': 1,
                    'timezone': 1,
                    'is_volunteer': 1,
                    'is_active': 1,
                    'telegram_username': 1,
                    'is_admin': 1,
                    'time_to_send_messages': 1,
                    'send_message': {
                        '$gte': [
                            '$hour_user', '$time_to_send_messages'
                        ]
                    }
                }
            }, {
                '$match': {
                    'send_message': True
                }
            }
        ])

    def get_user_by_id(self, id):
        return self.users.find_one({"_id": id})

    def get_user_by_telegram_id(self, id):
        return self.users.find_one({"telegram_id": id})
