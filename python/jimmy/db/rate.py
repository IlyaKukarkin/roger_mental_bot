from datetime import datetime

from singleton import SingletonClass


class Rate(object):
    def __init__(self):
        rate = SingletonClass().collection_name["rate"]

        self.rate = rate

    def insert_rate(self, user_id, message_id, rate):
        return self.rate.insert_one({"id_user": user_id, "id_message": message_id, "time_to_send": datetime.now(), "rate": rate})
