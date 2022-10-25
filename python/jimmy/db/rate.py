from datetime import datetime
import pytz

from singleton import SingletonClass


class Rate(object):
    def __init__(self):
        rate = SingletonClass().collection_name["rate"]

        self.rate = rate

    def get_today_rates_by_user(self, user_id):
        curr_date = datetime.now(pytz.utc)

        return self.rate.aggregate(
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

    def insert_rate(self, user_id, message_id, rate):
        return self.rate.insert_one({"id_user": user_id, "id_message": message_id, "time_to_send": datetime.now(), "rate": rate})
